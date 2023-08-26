# Genius Invokation TCG simulator

---

Backend of Genius Invokation TCG, written with Python using Pydantic and FastAPI.

This project is created for killing time.
No guarantee for progress and quality.

## usage

Currently not support text-based deck definition, need to define a 
deck based on `server.deck` module. `main.py` gives an example, but cards in
the deck are all the same.

Initialize a new `server.Match`, and use `set_deck` to set decks for players.
`Match.match_config` contains configurations of the match, modify it if needed.
After deck set, use `start` to start the match, it will initialize the match
based on the config and decks, then use `step` to move to next step, by 
default, `step` will continuously run until the match is ended or the match
generates requests and need response.

To make response, some simple agents are implemented in `agents`. You can use
agents to respond requests. `InteractionAgent` supports reading command lines
and generate responses, which can be used in console and in the frontend.

```python
from server.match import Match
from server.deck import Deck
from agents import RandomAgent
deck0 = Deck(**DECK)
deck1 = Deck(**DECK)
match = Match()
match.set_deck([deck0, deck1])
# match.match_config.max_same_card_number = 30  # disable deck limit
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

## feature

Pydantic to save & load states of match, exported data is complete to restore 
from certain state and continue running, and also easy for frontend to render
the game states.

Interact by request and response. When request list is not empty, agents need
to response to one of the request. When multiple players need to response,
their requests will be generated simultaneously.

All changes to the match table is done by actions. Every action will generate
a event and may activate new actions, and new action lists are added to the
top of all actions. It looks like a stack of lists of actions.

Object can add two types of triggers, the event handler and value modifier.
Event handler is used to listen events and return action lists. Value modifier
is used to modify modifiable values and update self states, for example, 
initial dice color, damage, cost.
