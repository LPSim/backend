# Genius Invokation TCG Simulator

---

Backend of Lochfolk Prinzessin Simulator, which simulates Genius Invokation 
TCG, written with Python using Pydantic and FastAPI.

This project is created for leisure, no guarantee for progress and quality.

This project is under AGPL-3.0 license.

## Usage

Currently package-like usage is not supported, please follow the following
instructions to run the project. 
This project support a frontend `zyr17/GITCG-frontend`. To use the frontend, 
please refer FastAPI section and readme of frontend.

Define decks for both players. Supports text-based or json-based deck 
definition. Refer to `server/deck.py` for details.

The outlines:

1. Initialize a fresh `server.Match` instance.
2. Use the `set_deck` function to assign decks for players.
3. Modify the `Match.match_config` if specific configurations are necessary.
4. Once the decks are set, initiate the match using the `Match.start` function. 
   This initializes the match according to the configurations and decks.
5. Progress through the match by employing the `Match.step` function. 
   By default, the step function will continually execute until the match 
   either ends or generates requests requiring responses.

In order to manage responses, the project includes a selection of simple 
agents within the `agents` module. These agents can generate 
responses to various requests. Notably, the `InteractionAgent` is equipped 
to interpret command lines and formulate responses. This proves useful both 
in console environments and within frontend interfaces.


```python
from server.match import Match
from server.deck import Deck
from agents import RandomAgent
deck_string = '''
charactor:Fischl*3
Stellar Predator*10
Strategize*10
Laurel Coronet*10
'''
deck0 = Deck.from_str(deck_string)
deck1 = Deck.from_str(deck_string)
match = Match()
match.set_deck([deck0, deck1])
match.match_config.max_same_card_number = 30  # disable deck limit
match.start()
match.step()

agent_0 = RandomAgent(player_id = 0)
agent_1 = RandomAgent(player_id = 1)

while not match.is_game_end():
    if match.need_respond(0):
        match.respond(agent_0.generate_response(match))
    elif match.need_respond(1):
        match.respond(agent_1.generate_response(match))
    match.step()

print(f'winner is {match.winner}')
```

## FastAPI

Use FastAPI to provide a web server, which can be used to interact with the
match. To run a server, use the following command:
```bash
uvicorn network:app --reload
```

It will open a FastAPI server on `localhost:8000`, and accepts connections
on `localhost:4000`, which is the port of frontend. Currently exception
management is chaos, errors may set game state to ERROR, raise Exception on
server side, make empty response on agent, return 404, or run JS failed on
frontend. Please open console of frontend and check the error message on both
sides.

## Feature

Pydantic to save & load states of match, exported data is complete to restore 
from certain state and continue running, and also easy for frontend to render
the game states.

Interact by request and response. When request list is not empty, agents need
to response to one of the request. When multiple players need to response,
(e.g. switch card and choose charactor at startup),
their requests will be generated simultaneously.

All modifications to the match table are orchestrated through actions. 
Each action triggers an event and has the potential to activate subsequent 
actions. These newly activated actions are appended to the top of the existing 
action list, akin to a stack structure.

Objects integrated into this system introduce two  types of triggers: event 
handlers and value modifiers. Event handlers function to monitor events and 
produce lists of actions in response. Value modifiers is used on edit 
mutable values and updating internal states if is necessary. Modifiable values
applies to attributes like initial dice color, damage, and cost.

## Contribution

Contributions are welcomed. To add a new charactor, please refer to
`server/charactor/electro/fischl.py` `server/charactor/hydro/mona.py`
and `server/charactor/dendro/nahida.py`. To add a new card, please refer to
existing card implementations.
