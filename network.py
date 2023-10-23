import logging
from typing import Any, Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.lpsim import Match, Deck
from tests.utils_for_test import get_random_state, set_16_omni, make_respond
from src.lpsim.agents import NothingAgent, InteractionAgent


HTTPServer = FastAPI()
logging.basicConfig(level = logging.INFO)


default_deck_str = '''
        default_version:4.1
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Dunyarzad*10
        Chef Mao*10
        Timmie*10
        Sweet Madame*10
'''
deck_str_1 = '''
charactor:Fischl@3.3
charactor:Rhodeia of Loch@3.3
charactor:Fatui Pyro Agent@3.3
Tubby@3.3
Sumeru City@3.7
Lucky Dog's Silver Circlet@3.3
Strategize@3.3
Leave It to Me!@3.3
Paid in Full@3.3
Sangonomiya Shrine@3.7
Lotus Flower Crisp@3.3
Mushroom Pizza@3.3
Favonius Cathedral@3.3
Mushroom Pizza@3.3
Magic Guide@3.3*19
'''
deck_str_2 = '''
charactor:Nahida@3.7
charactor:Rhodeia of Loch@3.3
charactor:Fischl@3.3
Gambler's Earrings@3.8
Paimon@3.3
Chef Mao@4.1
Dunyarzad@4.1
The Bestest Travel Companion!@3.3
Paimon@3.3
Liben@3.3
Liben@3.3
Send Off@3.7
Teyvat Fried Egg@4.1
Dunyarzad@4.1
Sweet Madame@3.3
I Haven't Lost Yet!@4.0
Send Off@3.7
Lotus Flower Crisp@3.3
Magic Guide@3.3*15
'''
# deck_str_1 = default_deck_str
# deck_str_2 = default_deck_str
match: Match = Match()
decks: list[Deck] = [Deck.from_str(deck_str_1), 
                     Deck.from_str(deck_str_2)]
# change HP
# for charactor in deck.charactors:
#     charactor.max_hp = 30
#     charactor.hp = 30


# Add the CORSMiddleware to the app
HTTPServer.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:4000', 'https://localhost:4000', 
        'http://127.0.0.1:4000', 'https://127.0.0.1:4000',
    ],
    # allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_new_match(seed: Any = None, rich: bool = False):
    if seed:
        match: Match = Match(random_state = seed)
    else:
        match: Match = Match()
    match.set_deck(decks)
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.random_first_player = False
    match.config.history_level = 10
    match.config.make_skill_prediction = True
    # match.config.initial_hand_size = 20
    # match.config.max_hand_size = 30
    match.config.check_deck_restriction = False
    match.config.recreate_mode = True
    match.config.random_object_information = {
        'rhodeia': ['squirrel', 'raptor', 'frog', 'squirrel', 'raptor', 'frog',
                    'frog', 'squirrel', 'squirrel']
    }
    match.config.player_go_first = 1
    if rich:
        set_16_omni(match)
    match.start()
    match._save_history()
    match.step()
    if agent_0.__class__ != InteractionAgent:
        while match.need_respond(0):
            make_respond(agent_0, match)
    return match


agent_0 = NothingAgent(player_idx = 0)
agent_0 = InteractionAgent(player_idx = 0, only_use_command = True)
agent_1 = InteractionAgent(player_idx = 1, only_use_command = True)


@HTTPServer.on_event('startup')
async def startup_event():
    global match
    match = get_new_match(seed = get_random_state(), rich = False)


class ResetData(BaseModel):
    fixed_random_seed: bool = False
    offset: int = 0
    rich_mode: bool = False
    match_state: Match | None = None
    match_state_idx: int | None = None


@HTTPServer.post('/reset')
async def reset(data: ResetData):
    """
    Reset the match. 
    If match_state_idx is not None, the match will be reset to the
    state of match_state_idx in history. This will keep histories before
    match_state_idx.
    Otherwise, if match_state is not None, the match will be reset to
    match_state. This will clear all histories and start with zero.
    Otherwise, a new match will be created, with 
    fixed_random_seed, offset and rich_mode.

    Return: The dict contains last state with its idx of the match if success.
    """
    global match
    fixed_random_seed = data.fixed_random_seed
    offset = data.offset
    rich = data.rich_mode
    match_state = data.match_state
    match_state_idx = data.match_state_idx
    if match_state_idx is not None:
        history = match._history[:]
        history_diff = match._history_diff[:]
        if len(history) <= match_state_idx or match_state_idx < 0:
            raise HTTPException(status_code = 404, detail = 'State not found')
        match = history[match_state_idx].copy(deep = True)
        match._history = history[:match_state_idx + 1]
        match._history_diff = history_diff[:match_state_idx + 1]
    elif match_state is not None:
        match = match_state
        match._save_history()
    else:
        if fixed_random_seed:
            random_seed = get_random_state(offset)
        else:
            random_seed = None
        match = get_new_match(seed = random_seed, rich = rich)
    return {
        'idx': match_state_idx,
        'match': match.dict(),
        'type': 'FULL',
    }


@HTTPServer.get('/deck/{player_idx}')
async def get_deck(player_idx: int):
    """
    get deck of a player.
    """
    if player_idx < 0 or player_idx > 1:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    return decks[player_idx].dict()


@HTTPServer.get('/decks')
async def get_decks():
    """
    get decks of both players.
    """
    return [deck.dict() for deck in decks]


class DeckData(BaseModel):
    deck_str: str
    player_idx: int


@HTTPServer.post('/deck')
async def post_deck(data: DeckData):
    """
    Set deck.
    """
    deck_str = data.deck_str
    player_idx = data.player_idx
    if player_idx < 0 or player_idx > 1:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    deck = Deck.from_str(deck_str)
    # if not match.state not in [MatchState.WAITING, 
    #                            MatchState.ENDED, 
    #                            MatchState.ERROR]:
    #     raise HTTPException(status_code = 403, detail = 'Match is running')
    if not deck.check_legal(
        match.config.card_number, match.config.max_same_card_number, 
        match.config.charactor_number, match.config.check_deck_restriction
    ):
        raise HTTPException(status_code = 403, detail = 'Deck not legal')
    global decks
    decks[player_idx] = deck


@HTTPServer.get('/state/{mode}/{state_idx}/{player_idx}')
async def get_game_state(
    mode: Literal['one', 'after'], state_idx: int, player_idx: int
):
    """
    Return list of state and its index.

    mode is one: only get the state of state_idx (but also wrapped in a list)
    mode is after: get the state of state_idx and all states after it

    state_idx: -1 means the last state; otherwise, it is the index of the state

    player_idx is -1: fetch complete data
    player_idx is 0 or 1: fetch data for player idx (currently not implemented)
    """
    # player idx check
    if player_idx < -1 or player_idx > 1:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    if player_idx != -1:
        raise HTTPException(status_code = 404, 
                            detail = 'player data fetch not suppoted')
    # state idx check
    if state_idx < -1 or state_idx > len(match._history):
        raise HTTPException(status_code = 404, detail = 'State not found')
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
        result += [{
            'idx': state_idx + 1 + idx,
            'match_diff': diff,
            'type': 'DIFF',
        } for idx, diff in enumerate(match._history_diff[state_idx + 1:])]
    print('state output length', len(result))
    return JSONResponse(result)


@HTTPServer.get('/request/{player_idx}')
async def get_request(player_idx: int):
    """
    Return the requests of player_idx. if player_idx is -1, return all 
    requests.
    """
    if player_idx < -1 or player_idx > 1:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    res = match.requests
    if player_idx != -1:
        res = [x for x in res if x.player_idx == player_idx]
    return JSONResponse([x.dict() for x in res])


class RespondData(BaseModel):
    player_idx: int
    command: str


@HTTPServer.post('/respond')
async def post_respond(data: RespondData):
    player_idx = data.player_idx
    command = data.command
    current_history_length = len(match._history)
    if not match.need_respond(player_idx):
        raise HTTPException(status_code = 404, detail = 'Not your turn')
    if player_idx == 0:
        agent = agent_0
    elif player_idx == 1:
        agent = agent_1
    else:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    if agent.__class__ == NothingAgent:
        raise HTTPException(status_code = 404, 
                            detail = 'Cannot control this agent')
    agent.commands = [command]
    resp = agent.generate_response(match)
    if resp is None:
        raise HTTPException(status_code = 404, detail = 'Invalid command')
    match.respond(resp)
    match.step()
    for agent in (agent_0, agent_1):
        if (
            agent.__class__ != InteractionAgent 
            or len(agent.commands) > 0  # type: ignore
        ):
            while match.need_respond(agent.player_idx):
                make_respond(agent, match)
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
