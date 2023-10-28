import json
from typing import Literal, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..server.match import Match, MatchConfig
from ..server.deck import Deck
from ..agents import InteractionAgent
from .utils import get_new_match


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


class HTTPServer():
    """
    Simple HTTP server based on HTTP API. No safety protocol and data 
    visibility support now, i.e. everyone can get full information of opponent
    player and system states.

    To check APIs, use /docs or /redoc after run the server.
    """
    def __init__(
        self, 
        allow_origins: List[str] = ['*'], 
        decks: List[Deck | str] = [],
        match_config: MatchConfig | None = None,
    ):
        self.app = FastAPI()
        self.decks = [Deck.from_str(deck) if isinstance(deck, str) else deck
                      for deck in decks]
        if match_config is not None and match_config.history_level < 10:
            raise ValueError(
                'history_level must be at least 10 for HTTPServer')
        self.match: Match = get_new_match(
            self.decks, match_config = match_config)
        self.agent_0 = InteractionAgent(player_idx = 0, 
                                        only_use_command = True)
        self.agent_1 = InteractionAgent(player_idx = 1, 
                                        only_use_command = True)

        if len(self.decks) == 0:
            # no deck input at init, create two empty decks.
            self.decks = [Deck.from_str('''''') for _ in range(2)]

        # attrs to save history. command is saved separately for two players,
        # and each line contains [idx, command], idx is idx of last history.
        self.command_history = [[], []]
        self.match_random_state = self.match.random_state
        self.start_deck = self.decks[:]

        app = self.app
        # Add the CORSMiddleware to the app
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            # allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        # @app.on_event('startup')
        # async def startup_event():
        #     self.match = get_new_match(
        #         decks = self.decks,
        #         rich_mode = False
        #     )

        '''API hanlders for app'''

        @app.post('/reset')
        async def reset(data: ResetData):
            """
            Reset the match. 
            If match_state_idx is not None, the match will be reset to the
            state of match_state_idx in history. This will keep histories 
            before match_state_idx.
            Otherwise, if match_state is not None, the match will be reset to
            match_state. This will clear all histories and start with zero.
            Otherwise, a new match will be created, with 
            fixed_random_seed, offset and match_config and rich_mode. Note when
            match_config is None, current match_config in self.match will be
            used.

            Return: The dict contains last state with its idx of the match if 
                success.
            """
            match = self.match
            fixed_random_seed = data.fixed_random_seed
            if fixed_random_seed:
                raise NotImplementedError('fixed_random_seed not supported')
            match_config = data.match_config
            if match_config is None:
                match_config = match.config
            rich = data.rich_mode
            match_state = data.match_state
            match_state_idx = data.match_state_idx
            if match_state_idx is not None:
                history = match._history[:]
                history_diff = match._history_diff[:]
                if len(history) <= match_state_idx or match_state_idx < 0:
                    raise HTTPException(status_code = 404, 
                                        detail = 'State not found')
                match = history[match_state_idx].copy(deep = True)
                match._history = history[:match_state_idx + 1]
                match._history_diff = history_diff[:match_state_idx + 1]
                self.match = match
                # remove command history that after match_state_idx. No need to
                # change match random state and start deck.
                current_cmd_hist = self.command_history[:]
                self.command_history = [[], []]
                for source, target in zip(current_cmd_hist,
                                          self.command_history):
                    for idx, cmd in source:
                        if idx >= match_state_idx:
                            break
                        target.append([idx, cmd])
            elif match_state is not None:
                match = match_state
                match._save_history()
                match_state_idx = len(match._history) - 1
                # when reset by match_state, cannot record history with only
                # match random state, set to None to notify that cannot save.
                self.command_history = [[], []]
                self.match_random_state = None
                self.start_deck = [x.player_deck_information 
                                   for x in match.player_tables]
            else:
                self.match = get_new_match(
                    decks = self.decks,
                    rich_mode = rich,
                    match_config = match_config,
                )
                match_state_idx = 0
                match = self.match
                self.command_history = [[], []]
                self.match_random_state = self.match.random_state
                self.start_deck = [x.player_deck_information 
                                   for x in match.player_tables]
            return {
                'idx': match_state_idx,
                'match': match.dict(),
                'type': 'FULL',
            }

        @app.get('/deck/{player_idx}')
        async def get_deck(player_idx: int):
            """
            get deck of a player.
            """
            if player_idx < 0 or player_idx > 1:
                raise HTTPException(status_code = 404, 
                                    detail = 'Player not found')
            return self.decks[player_idx].dict()

        @app.get('/decks')
        async def get_decks():
            """
            get decks of both players.
            """
            return [deck.dict() for deck in self.decks]

        @app.post('/deck')
        async def post_deck(data: DeckData):
            """
            Set deck.
            """
            match = self.match
            deck_str = data.deck_str
            player_idx = data.player_idx
            if player_idx < 0 or player_idx > 1:
                raise HTTPException(status_code = 404, 
                                    detail = 'Player not found')
            deck = Deck.from_str(deck_str)
            if not deck.check_legal(
                match.config.card_number, 
                match.config.max_same_card_number, 
                match.config.charactor_number, 
                match.config.check_deck_restriction
            ):
                raise HTTPException(status_code = 403, 
                                    detail = 'Deck not legal')
            self.decks[player_idx] = deck

        @app.get('/state/{mode}/{state_idx}/{player_idx}')
        async def get_game_state(
            mode: Literal['one', 'after'], state_idx: int, player_idx: int
        ):
            """
            Return list of state and its index.

            mode is one: only get the state of state_idx (but also wrapped in a
                list)
            mode is after: get the state of state_idx and all states after it

            state_idx: -1 means the last state; otherwise, it is the index of 
                the state

            player_idx is -1: fetch complete data
            player_idx is 0 or 1: fetch data for player idx (currently not 
                implemented)
            """
            match = self.match
            # player idx check
            if player_idx < -1 or player_idx > 1:
                raise HTTPException(status_code = 404, 
                                    detail = 'Player not found')
            if player_idx != -1:
                raise HTTPException(status_code = 404, 
                                    detail = 'player data fetch not suppoted')
            # state idx check
            if state_idx < -1 or state_idx > len(match._history):
                raise HTTPException(status_code = 404, 
                                    detail = 'State not found')
            if state_idx == -1:
                state_idx = len(match._history) - 1
            if state_idx == len(match._history):
                # ask for the state after the last state
                return JSONResponse([])
            result = [{
                'idx': state_idx,
                'match': match._history[state_idx].dict(),
                'type': 'FULL',
            }]
            if mode == 'after':
                result += [
                    {
                        'idx': state_idx + 1 + idx,
                        'match_diff': diff,
                        'type': 'DIFF',
                    } 
                    for idx, diff 
                    in enumerate(match._history_diff[state_idx + 1:])
                ]
            print('state output length', len(result))
            return JSONResponse(result)

        @app.get('/request/{player_idx}')
        async def get_request(player_idx: int):
            """
            Return the requests of player_idx. if player_idx is -1, return all 
            requests.
            """
            if player_idx < -1 or player_idx > 1:
                raise HTTPException(status_code = 404, 
                                    detail = 'Player not found')
            res = self.match.requests
            if player_idx != -1:
                res = [x for x in res if x.player_idx == player_idx]
            return JSONResponse([x.dict() for x in res])

        @app.post('/respond')
        async def post_respond(data: RespondData):
            match = self.match
            player_idx = data.player_idx
            command = data.command
            current_history_length = len(match._history)
            if not match.need_respond(player_idx):
                raise HTTPException(status_code = 404, 
                                    detail = 'Not your turn')
            if player_idx == 0:
                agent = self.agent_0
            elif player_idx == 1:
                agent = self.agent_1
            else:
                raise HTTPException(status_code = 404, 
                                    detail = 'Player not found')
            agent.commands = [command]
            resp = agent.generate_response(match)
            if resp is None:
                raise HTTPException(status_code = 404, 
                                    detail = 'Invalid command')
            match.respond(resp)
            match.step()
            for agent in (self.agent_0, self.agent_1):
                if (
                    agent.__class__ != InteractionAgent 
                    or len(agent.commands) > 0  # type: ignore
                ):
                    while match.need_respond(agent.player_idx):
                        resp = agent.generate_response(match)
                        assert resp is not None
                        match.respond(resp)
                        match.step()
            # after success respond, save command into command history
            self.command_history[player_idx].append([
                current_history_length - 1, command
            ])
            # generate response
            ret = []
            for idx, [state, diff] in enumerate(zip(
                    match._history[current_history_length:],
                    match._history_diff[current_history_length:],)):
                if idx == 0:
                    ret.append({
                        'idx': idx + current_history_length,
                        'match': state.dict(),
                        'type': 'FULL',
                    })
                else:
                    ret.append({
                        'idx': idx + current_history_length,
                        'match_diff': diff,
                        'type': 'DIFF',
                    })
            return JSONResponse(ret)

        @app.get('/log')
        def get_log():
            """
            Return the log of the match. It is encoded in json.
            """
            try:
                log = self.save_log()
                return json.loads(log)
            except Exception as e:
                raise HTTPException(status_code = 500, detail = str(e))

    def run(self, *argv, **kwargs):
        """
        A wrapper of uvicorn.run
        """
        if len(argv):
            raise ValueError('positional arguments not supported')
        uvicorn.run(self.app, **kwargs)

    def save_log(self, file_path: str | None = None) -> str:
        """
        Save the log to specified file and return log str.
        If file path not specified, only return log str.
        log str is encoded in json.

        log format:
            match_random_state: initial random state of match
            start_deck: start deck string of players
            command_history: command history of players, different from
                self.command_history, it do not contain idx of history.
        """
        if self.match_random_state is None:
            raise RuntimeError('Cannot save log when match random state is '
                               'None. This may caused by reset match by '
                               'match_state.')
        data = {
            'match_random_state': self.match_random_state,
            'start_deck': [x.to_str() for x in self.start_deck],
            'command_history': [[y[1] for y in x] 
                                for x in self.command_history],
        }
        data_str = json.dumps(data)
        if file_path is not None:
            with open(file_path, 'w') as f:
                f.write(data_str)
        return data_str
