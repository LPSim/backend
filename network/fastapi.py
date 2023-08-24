from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server.match import Match
from server.deck import Deck
from tests.utils_for_test import get_random_state, set_16_omni, make_respond
from agents.nothing_agent import NothingAgent
from agents.interaction_agent import InteractionAgent


app = FastAPI()


# Add the CORSMiddleware to the app
app.add_middleware(
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
    TEST_DECK = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
                'hp': 99,
                'max_hp': 99,
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**TEST_DECK)
    if seed:
        match: Match = Match(random_state = seed)
    else:
        match: Match = Match()
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    if rich:
        set_16_omni(match)
    match.start()
    match.step()
    return match


agent_0 = NothingAgent(player_id = 0)
agent_1 = InteractionAgent(player_id = 1, only_use_command = True)


@app.on_event('startup')
async def startup_event():
    global match
    match = get_new_match()


@app.post('reset')
async def reset(fixed_random_seed: bool = False, offset: int = 0, 
                rich: bool = False):
    global match
    if fixed_random_seed:
        random_seed = get_random_state(offset)
    else:
        random_seed = None
    match = get_new_match(seed = random_seed, rich = rich)


@app.get('/state/{player_id}')
async def get_game_state(player_id: int):
    if player_id < 0 or player_id > 1:
        raise HTTPException(status_code = 404, detail = 'Player not found')
    if player_id == 0:
        raise HTTPException(status_code = 404, 
                            detail = 'player 0 not suppoted')
    return JSONResponse(match.dict())


class RespondData(BaseModel):
    player_id: int
    command: str


@app.post('/respond')
async def post_respond(data: RespondData):
    player_id = data.player_id
    command = data.command
    if not match.need_respond(player_id):
        raise HTTPException(status_code = 404, detail = 'Not your turn')
    if player_id != 1:
        raise HTTPException(status_code = 404, 
                            detail = 'player 0 not supported')
    agent_1.commands = [command]
    resp = agent_1.generate_response(match)
    if resp is None:
        raise HTTPException(status_code = 404, detail = 'Invalid command')
    match.respond(resp)
    match.step()
    while match.need_respond(0):
        make_respond(agent_0, match)
    return JSONResponse(match.dict())
