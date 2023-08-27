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
    deck = Deck.from_str('''
        charactor:Mona*2
        charactor:Fischl
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
    ''')
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
agent_0 = InteractionAgent(player_id = 0, only_use_command = True)
agent_1 = InteractionAgent(player_id = 1, only_use_command = True)


@app.on_event('startup')
async def startup_event():
    global match
    match = get_new_match(seed = get_random_state(), rich = False)


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
    # if player_id != 1:
    #     raise HTTPException(status_code = 404, 
    #                         detail = 'player 0 not supported')
    if player_id == 0:
        agent = agent_0
    elif player_id == 1:
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
        if agent.__class__ != InteractionAgent or len(agent.commands) > 0:
            while match.need_respond(agent.player_id):
                make_respond(agent, match)
    return JSONResponse(match.dict())
