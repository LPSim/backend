import asyncio
import logging
import json
import uuid
import os
import time
import datetime
from typing import Literal, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import uvicorn

from ..utils.desc_registry import get_desc_patch

from ..server.match import Match, MatchConfig
from ..server.deck import Deck
from ..agents import InteractionAgent
from .utils import get_new_match
from ..utils.deck_code import deck_code_data
from .__version__ import __version_tuple__, __version__, __frontend_version__


class EndpointFilter(logging.Filter):
    """Filter class to exclude specific endpoints from log entries."""

    def __init__(self, excluded_endpoints: list[str]) -> None:
        """
        Initialize the EndpointFilter class.

        Args:
            excluded_endpoints (list[str]): A list of endpoints to be excluded from log
                entries.
        """
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out log entries for excluded endpoints.

        Args:
            record (logging.LogRecord): The log record to be filtered.

        Returns:
            bool: True if the log entry should be included, False otherwise.
        """
        if record.args and len(record.args) >= 3:
            endpoint: str = record.args[2]  # type: ignore
            for excluded_endpoint in self.excluded_endpoints:
                if endpoint.startswith(excluded_endpoint):
                    return False
            return True
        return False


class ResetData(BaseModel):
    fixed_random_seed: bool = False
    offset: int = 0
    match_config: MatchConfig | None = None
    rich_mode: bool = False
    match_state: Match | None = None
    match_state_idx: int | None = None


class DeckData(BaseModel):
    deck_str: str
    player_idx: int


class RespondData(BaseModel):
    player_idx: int
    command: str
    uuid: str
    frame_number: int = -1


class HTTPServer:
    """
    Simple HTTP server based on HTTP API. No safety protocol and data
    visibility support now, i.e. everyone can get full information of opponent
    player and system states.

    To check APIs, use /docs or /redoc after run the server.
    """

    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        decks: List[Deck | str] = [],
        match_config: MatchConfig | None = None,
        reset_log_save_path: str | None = None,
        room_name: str = "",
        excluded_log_endpoints: List[str] = ["/request", "/state"],
        get_state_timeout: float = 10,
        get_state_sleeptime: float = 0.5,
    ):
        """
        Init the HTTPServer instance.

        Args:
            allow_origins (List[str]): list of allowed origins, default is ['*']
            decks (List[Deck | str]): list of decks of players, each element can be a
                string or a Deck object. If a string, it will be parsed to a Deck
                object.
            match_config (MatchConfig): match config of the match, default is None,
                which means use default config.
            reset_log_save_path (str): if not None, save the log when reset match to the
                path. The log is encoded in json, and log name is the timestamp.
            room_name (str): name of the room. If not empty, only request with
                room=room_name will be accepted.
            excluded_log_endpoints (List[str]): endpoints that will not be logged.
                Default is ['/request', '/state'].
        """
        self.app = FastAPI()
        self.decks = [
            Deck.from_str(deck) if isinstance(deck, str) else deck for deck in decks
        ]
        self.reset_log_save_path = reset_log_save_path
        self.room_name = room_name
        self.excluded_log_endpoints = excluded_log_endpoints
        # timeout and sleeptime for long polling get state. If do not want to
        # perform long polling, set timeout to less than 0.
        self.get_state_timeout = get_state_timeout
        self.get_state_sleeptime = get_state_sleeptime
        logging.getLogger("uvicorn.access").addFilter(
            EndpointFilter(self.excluded_log_endpoints)
        )
        if match_config is not None and match_config.history_level < 10:
            raise ValueError("history_level must be at least 10 for HTTPServer")
        match, random_state = get_new_match(self.decks, match_config=match_config)
        self.uuid = str(uuid.uuid4())
        self.match = match
        self.match_random_state = random_state
        self.agent_0 = InteractionAgent(player_idx=0, only_use_command=True)
        self.agent_1 = InteractionAgent(player_idx=1, only_use_command=True)
        # used to record all uploaded deck codes to the server
        self.uploaded_deck_codes = []

        if len(self.decks) == 0:
            # no deck input at init, create two empty decks.
            self.decks = [Deck.from_str("""""") for _ in range(2)]

        # attrs to save history. command is saved separately for two players,
        # and each line contains [idx, command], idx is idx of last history.
        self.command_history = [[], []]
        self.start_deck = self.decks[:]

        app = self.app
        # Add the CORSMiddleware to the app
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            # allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Add the GZipMiddleware to the app
        app.add_middleware(GZipMiddleware)

        @app.middleware("http")
        async def check_room_name(request: Request, call_next):
            query_params = request.query_params
            if self.room_name != "" and (
                "room" not in query_params or query_params["room"] != self.room_name
            ):
                return JSONResponse(status_code=404, content="Room name wrong")
            response = await call_next(request)
            return response

        """API handlers for app"""

        @app.get("/version")
        async def get_version():
            """
            Return the version of lpsim.

            Return:
                version: version string
                version_tuple: version tuple
                support_version: support version of frontend
                info: information of the server
            """
            return {
                "version": __version__,
                "version_tuple": __version_tuple__,
                "support_version": __frontend_version__,
                "info": {
                    "class": "HTTPServer",
                },
            }

        @app.get("/patch")
        async def get_patch():
            """
            Return the desc patch.

            Return:
                version: version string
                patch: patch dict, which contains all descriptions with type
                    `Dict[str, DescDictType]`.
            """
            patch = get_desc_patch()
            return {"version": "1.0", "patch": patch}

        @app.post("/reset")
        async def post_reset(data: ResetData):
            """
            Reset the match.
            If match_state_idx is not None, the match will be reset to the
            state of match_state_idx in history. This will keep histories
            before match_state_idx.

            Otherwise, if match_state is not None, the match will be reset to
            match_state. This will clear all histories and start with zero.
            (Currently not implemented).

            Otherwise, a new match will be created, with
            fixed_random_seed, offset and match_config and rich_mode. Note when
            match_config is None, current match_config in self.match will be
            used.

            The return has same structure as state API.

            If it is a full match, four
            fields will be returned: uuid, idx, match and type. Here match is the
            full match state, which is parsed from `Match` directly.

            If it is a diff match, four fields will be returned: uuid, idx, match_diff
            and type. Here match_diff is the diff of the match state, which is
            generated by dictdiffer, to describe difference between two match
            states. Note that frontend show frames totally based on matches, so
            need to generate multiple diffs to show multiple changes (e.g. using skill
            may generate UseSkill, MakeDamage, DrawCard, etc. multiple frames).

            Return:
                uuid: uuid of the match
                idx: index of the match state
                match: full match state
                type: "FULL"
            """
            self.save_log(self.reset_log_save_file)
            match = self.match
            fixed_random_seed = data.fixed_random_seed
            if fixed_random_seed:
                raise NotImplementedError("fixed_random_seed not supported")
            match_config = data.match_config
            if match_config is None:
                match_config = match.config
            rich = data.rich_mode
            match_state = data.match_state
            match_state_idx = data.match_state_idx
            if match_state_idx is not None:
                try:
                    match = self.match.new_match_from_history(match_state_idx)
                except AssertionError as e:
                    raise HTTPException(status_code=404, detail=str(e))
                self.match = match
                # remove command history that after match_state_idx. No need to
                # change match random state and start deck.
                current_cmd_hist = self.command_history[:]
                self.command_history = [[], []]
                for source, target in zip(current_cmd_hist, self.command_history):
                    for idx, cmd, order in source:
                        if idx >= match_state_idx:
                            break
                        target.append([idx, cmd, order])
            elif match_state is not None:
                match = match_state
                match._save_history()
                match_state_idx = len(match._history_diff) - 1
                # when reset by match_state, cannot record history with only
                # match random state, set to None to notify that cannot save.
                self.command_history = [[], []]
                self.match_random_state = None
                self.start_deck = [
                    x.player_deck_information for x in match.player_tables
                ]
            else:
                self.match, self.match_random_state = get_new_match(
                    decks=self.decks,
                    rich_mode=rich,
                    match_config=match_config,
                )
                match_state_idx = 0
                match = self.match
                self.command_history = [[], []]
                self.start_deck = [
                    x.player_deck_information for x in match.player_tables
                ]
            self.uuid = str(uuid.uuid4())
            return {
                "uuid": self.uuid,
                "idx": match_state_idx,
                "match": match.dict(),
                "type": "FULL",
            }

        @app.get("/deck/{player_idx}")
        async def get_deck(player_idx: int):
            """
            get deck of a player.

            Args:
                player_idx (int): index of the player, 0 or 1.

            Return:
                deck: deck of the player, which directly parsed from `Deck` object.
            """
            if player_idx < 0 or player_idx > 1:
                raise HTTPException(status_code=404, detail="Player not found")
            return self.decks[player_idx].dict()

        @app.get("/decks")
        async def get_decks():
            """
            get decks of both players.

            Return:
                list of decks of both players.
            """
            return [deck.dict() for deck in self.decks]

        def post_deck_data(data: DeckData, str_type: Literal["str", "code"]):
            match = self.match
            deck_str = data.deck_str
            player_idx = data.player_idx
            if player_idx < 0 or player_idx > 1:
                raise HTTPException(status_code=404, detail="Player not found")
            if str_type == "str":
                deck = Deck.from_str(deck_str)
            else:
                try:
                    deck = Deck.from_deck_code(deck_str)
                except Exception:
                    raise HTTPException(status_code=403, detail="Invalid deck code")
            deck_check_res, deck_check_info = deck.check_legal(
                match.config.card_number,
                match.config.max_same_card_number,
                match.config.character_number,
                match.config.check_deck_restriction,
            )
            if not deck_check_res:
                raise HTTPException(
                    status_code=403, detail=f"Deck not legal. {deck_check_info}"
                )
            self.decks[player_idx] = deck
            try:
                deck_code = deck.to_deck_code()
                self.uploaded_deck_codes.append(deck_code)
            except Exception:
                pass

        @app.post("/deck")
        async def post_deck(data: DeckData):
            """
            Set deck.

            Args:
                data (DeckData): deck data, which contains deck_str and player_idx.
                    Note that deck_str is deck string.
            """
            post_deck_data(data, "str")

        @app.get("/deck_code/{player_idx}")
        async def get_deck_code(player_idx: int):
            """
            get deck code of a player.

            Args:
                player_idx (int): index of the player, 0 or 1.

            Return:
                deck_code: deck code of the player, which is a string.
            """
            if player_idx < 0 or player_idx > 1:
                raise HTTPException(status_code=404, detail="Player not found")
            try:
                return self.decks[player_idx].to_deck_code()
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))

        @app.post("/deck_code")
        async def post_deck_code(data: DeckData):
            """
            Set deck by deck code.

            Args:
                data (DeckData): deck data, which contains deck_str and player_idx.
                    Note that deck_str is deck code.
            """
            post_deck_data(data, "code")

        @app.get("/deck_code_data")
        async def get_deck_code_data():
            """
            get deck code data that is needed for generating deckcode in
            frontend.
            """
            return JSONResponse(deck_code_data)

        @app.get("/state/{mode}/{state_idx}/{player_idx}")
        async def get_game_state(
            mode: Literal["one", "after"],
            state_idx: int,
            player_idx: int,
            uuid: str | None = None,
        ):
            """
            Return list of state and its index.

            Args:
                mode (Literal["one", "after"]): mode of fetching state.
                    If mode is one, only get the state of state_idx (but also wrapped
                    in a list)
                    If mode is after: get the state of state_idx and all states after
                    it.

                state_idx (int): -1 means the last state; otherwise, it is the index of
                    the state

                player_idx (int): -1 means fetch complete data; 0 or 1 means fetch data
                    for player idx (currently not implemented)

            Return:
                list of states. For detail of state dict, refer to `post_reset`.
            """
            if state_idx > 0 and uuid != self.uuid:
                # not initial state, but uuid different
                raise HTTPException(status_code=404, detail="UUID not match")
            match = self.match
            # player idx check
            if player_idx < -1 or player_idx > 1:
                raise HTTPException(status_code=404, detail="Player not found")
            if player_idx != -1:
                raise HTTPException(
                    status_code=404, detail="player data fetch not supported"
                )
            # state idx check
            if state_idx < -1 or state_idx > len(match._history_diff):
                raise HTTPException(status_code=404, detail="State not found")
            if state_idx == -1:
                state_idx = len(match._history_diff) - 1
            start_time = time.time()
            while time.time() - start_time < self.get_state_timeout:
                if state_idx > 0 and self.uuid != uuid:
                    # during waiting data change, uuid changed. new match
                    # started, return empty result
                    return JSONResponse([])
                if state_idx == len(match._history_diff):
                    # ask for the state after the last state, wait until
                    # timeout to try to get new state
                    await asyncio.sleep(self.get_state_sleeptime)
                    continue
                result = []
                if state_idx == 0:
                    # first is 0, add full state and change state_idx to 1
                    result = [
                        {
                            "uuid": self.uuid,
                            "idx": state_idx,
                            "match": match._history[0].dict(),
                            "type": "FULL",
                        }
                    ]
                    state_idx = 1
                if mode == "after":
                    result += [
                        {
                            "uuid": self.uuid,
                            "idx": state_idx + idx,
                            "match_diff": diff,
                            "type": "DIFF",
                        }
                        for idx, diff in enumerate(match._history_diff[state_idx:])
                    ]
                return JSONResponse(result)
            return JSONResponse([])

        @app.get("/request/{player_idx}")
        async def get_request(player_idx: int):
            """
            Return the requests of player_idx. if player_idx is -1, return all
            requests. Sometimes We will update requests, but should not generate a new
            state, for example when choosing who goes first at startup. With this API,
            we can get the newest requests even if the last state is not changed.
            """
            if player_idx < -1 or player_idx > 1:
                raise HTTPException(status_code=404, detail="Player not found")
            res = self.match.requests
            if player_idx != -1:
                res = [x for x in res if x.player_idx == player_idx]
            return JSONResponse([x.dict() for x in res])

        @app.post("/respond")
        async def post_respond(data: RespondData):
            """
            Receives respond to the request. Respond command string will be sent to
            `InteractionAgent`.
            """
            if data.uuid != self.uuid:
                raise HTTPException(status_code=404, detail="UUID not match")
            if data.frame_number != -1:
                # contains frame number, should match with current frame number
                if data.frame_number + 1 < len(self.match._history_diff):
                    # old respond, ignore
                    return JSONResponse([])
            match = self.match
            player_idx = data.player_idx
            command = data.command
            current_history_length = len(match._history_diff)
            if not match.need_respond(player_idx):
                raise HTTPException(status_code=404, detail="Not your turn")
            if player_idx == 0:
                agent = self.agent_0
            elif player_idx == 1:
                agent = self.agent_1
            else:
                raise HTTPException(status_code=404, detail="Player not found")
            agent.commands = [command]
            resp = agent.generate_response(match)
            if resp is None:
                raise HTTPException(status_code=404, detail="Invalid command")
            match.respond(resp)
            match.step()
            for agent in (self.agent_0, self.agent_1):
                if (
                    agent.__class__ != InteractionAgent or len(agent.commands) > 0  # type: ignore  # noqa: E501
                ):
                    while match.need_respond(agent.player_idx):
                        resp = agent.generate_response(match)
                        assert resp is not None
                        match.respond(resp)
                        match.step()
            # after success respond, save command into command history
            self.command_history[player_idx].append(
                [
                    current_history_length - 1,
                    command,
                    len(self.command_history[0] + self.command_history[1]),
                ]
            )
            # generate response
            ret = []
            for idx, diff in enumerate(match._history_diff[current_history_length:]):
                if idx == 0 and current_history_length == 0:
                    ret.append(
                        {
                            "uuid": self.uuid,
                            "idx": idx + current_history_length,
                            "match": match._history[0].dict(),
                            "type": "FULL",
                        }
                    )
                else:
                    ret.append(
                        {
                            "uuid": self.uuid,
                            "idx": idx + current_history_length,
                            "match_diff": diff,
                            "type": "DIFF",
                        }
                    )
            return JSONResponse(ret)

        @app.get("/log")
        def get_log():
            """
            Return the log of the match. It is encoded in json.
            """
            try:
                log = self.save_log()
                return json.loads(log)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def run(self, *argv, **kwargs):
        """
        A wrapper of uvicorn.run
        """
        if len(argv):
            raise ValueError("positional arguments not supported")
        uvicorn.run(self.app, **kwargs)

    @property
    def reset_log_save_file(self) -> str | None:
        """
        Return the save file path of reset log.
        """
        # save log
        if self.reset_log_save_path is None:
            return None
        if not os.path.exists(self.reset_log_save_path):
            os.makedirs(self.reset_log_save_path)
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        filename += ".json"
        return os.path.join(self.reset_log_save_path, filename)

    def save_log(self, file_path: str | None = None) -> str:
        """
        Save the log to specified file and return log str.
        If file path not specified, only return log str.
        log str is encoded in json.

        log format:
            match_random_state: initial random state of match
            start_deck: start deck string of players
            command_history: command history of players.
        """
        if self.match_random_state is None:
            raise RuntimeError(
                "Cannot save log when match random state is "
                "None. This may caused by reset match by "
                "match_state."
            )
        data = {
            "match_random_state": self.match_random_state,
            "start_deck": [x.to_str() for x in self.start_deck],
            "command_history": self.command_history,
            "match_config": self.match.config.dict(),
        }
        data_str = json.dumps(data)
        if file_path is not None:
            with open(file_path, "w") as f:
                f.write(data_str)
        return data_str
