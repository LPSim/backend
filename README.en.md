# Lochfolk Prinzessin Simulator (LPSim): A Genius Invokation TCG Simulator

---

[![Coverage Status](https://coveralls.io/repos/github/LPSim/backend/badge.svg?branch=master)](https://coveralls.io/github/LPSim/backend?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/lpsim.svg?color=blue)](https://pypi.org/project/lpsim/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Backend of Lochfolk Prinzessin Simulator, which simulates Genius Invokation 
TCG, written with Python 3.10 using Pydantic and FastAPI. This project has
another [frontend repository](https://github.com/LPSim/frontend) which contains 
a frontend page to interact with this backend.

This project is under AGPL-3.0 license. If you have any secondary development
and distribution based on this project, please comply with this license.

## Disclaimer

This project is for learning and communication only. The frontend is only used
for displaying game states and debugging, and you should delete all related 
files in 24 hours after downloading. All related codes are open source
under AGPLv3 license. This project is not related to miHoYo, and all game
materials are owned by miHoYo. This project and its code repository do not
contain any image materials owned by miHoYo, or any non-public information
related to miHoYo products.

## Progress

:sparkles: 4.5 characters and cards, as well as balance changes are 
implemented.

:hammer: 4.6 characters and cards, as well as balance changes are
being implemented, including strategies related to deck order.

:construction: AI training support is being implemented, refer to AI training
support section.

## Feature

- All characters and cards with latest version are implemented.
- Support using different version of characters and cards in a same deck.
- Support serve as a mini server to interact with the match.
- A frontend is provided to interact with the server.
- Consistent when load from a state and continue running.
- 100% Coverage of codes.


## :construction: WIP: AI Training Support

Using LPSim as a simulator for AI training has the following advantages:
1. Since all card versions are implemented internally, updates to the simulator and official balance changes will have little impact on previously trained AI strategies. Old card versions and strategies can be used at any time to play against new card versions and strategies (if the old strategy does not fail due to the opponent using new cards).
2. The code is implemented in Python, making it easy to integrate into common deep learning frameworks such as PyTorch and TensorFlow.
3. All simulation processes are implemented by class functions of the Match class, without multi-threading or network communication, making it easy to implement environment parallelization.
4. Based on Pydantic, Match can import and export from any time without changing the subsequent simulation results, making it easy to reproduce and debug.
5. Some basic agents have been implemented, which can be used to quickly build a single-agent environment; at the same time, interactive agents have been designed to facilitate training and playing against them after training.

Currently, the environment definition based on `gymnasium` and `pettingzoo` has been developed, including `gymnasium.Env`, `pettingzoo.AECEnv` basic environments. Since how to accurately represent the state of Genius Invokation as an array is a difficult problem, the basic environment has not yet implemented the encoding representation of the state, and can be inherited from the environment for modification or use `Wrapper` to modify the observation and action space.

In the `src/lpsim/env` folder of the [pettingzoo](https://github.com/LPSim/backend/tree/pettingzoo) branch, the above environment implementation is included, as well as simple test code under the [Tianshou]([https://](https://github.com/thu-ml/tianshou)) multi-agent framework. The environment has not been thoroughly tested at present, and currently exists as an independent branch with the possibility of interface changes. AI-related code is currently only tested in Python 3.10, and its availability in other python versions is not guaranteed.

## Usage

This project works with Python 3.10 or newer.

### Installation by pip

To install the newest release version, use `pip install lpsim`. You can find
the newest release version on [PyPI](https://pypi.org/project/lpsim/), and
you can find the change log on [CHANGELOG.md](CHANGELOG.md).

To install the newest development version, use 
`pip install lpsim -i https://test.pypi.org/simple/`. When new commits are
pushed to `master` branch and pass all tests, a new version will be released 
on test PyPI. When new tag is pushed to `master` branch, a new version will be
released on PyPI.

### Installation by source

Clone this repository and install the package by `pip install .`. 

### HTTP Server

Use FastAPI to provide a HTTP server, which can be used to interact with the
match. To run a server, use the following command:
```
from lpsim.network import HTTPServer
server = HTTPServer()
server.run()
```

It will open a FastAPI server on `localhost:8000`, and accept connections
from localhost. When initialize HTTPServer, you can set decks and match configs
to create a match with specified rules.

To start the match, open a 
[frontend web page](https://lpsim.github.io/frontend), change server
URL on top right (default is `http://localhost:8000`), and follow the 
instructions on the page to set Deck and start match between two players.

Currently exception
management is chaos, errors may set game state to ERROR, raise Exception on
server side, make empty response on agent, return 404/500, or run JS failed on
frontend. Please open console of frontend and check the error message on both
sides.

#### Room Server

You can serve multiple matches by using room server. It manages multiple
HTTP server instances, frontend can create new room and join existing room.
When a new room is created, room server will tell frontend the room name and
the port it runs, then frontend will connect to the HTTP server on that port.
When a room is created for a long time and no POST request is received, it
will be closed automatically. Refer to `lpsim/network/http_room_server.py` and
`http_room_serve.py` for more details.

### Start a match non-interactively

#### Define the deck

To start a match, you should firstly 
define decks for both players. Supports text-based or json-based deck 
definition. Usually, `Deck.from_str` is enough to define a deck, which contains
characters and cards definition, and can control their versions. The deck 
string in the following sample code shows the syntax of deck definition,
all cards are based on 4.1 version, except Wind and Freedom, which is based on
4.0 version (As it has not changed after 3.7, when specify version 4.0, deck
will automatically choose 3.7 version).
Refer to `server/deck.py` for details.

#### Run the match

1. Initialize a fresh `server.Match` instance.
2. Use the `set_deck` function to assign decks for players.
3. Modify the `Match.config` if specific configurations are necessary.
4. Once the decks are set, initiate the match using the `Match.start` function. 
   This initializes the match according to the configurations and decks.
   If error occurred (e.g. deck is not valid), it will return False and detailed 
   error message.
5. Progress through the match by employing the `Match.step` function. 
   By default, the step function will continually execute until the match 
   either ends or generates requests requiring responses.

In order to manage responses, the project includes a selection of simple 
agents within the `agents` module. These agents can generate 
responses to various requests. Notably, the `InteractionAgent` is equipped 
to interpret command lines and formulate responses. This is useful both 
in console environments and within frontend interfaces.

#### Sample code

```python
from lpsim import Match, Deck
from lpsim.agents import RandomAgent
deck_string = '''
default_version:4.1
character:Fischl
character:Mona
character:Nahida
Gambler's Earrings*2
Wine-Stained Tricorne*2
Vanarana
Timmie*2
Rana*2
Covenant of Rock
Wind and Freedom@4.0
The Bestest Travel Companion!*2
Changing Shifts*2
Toss-Up
Strategize*2
I Haven't Lost Yet!*2
Leave It to Me!
Calx's Arts*2
Adeptus' Temptation*2
Lotus Flower Crisp*2
Mondstadt Hash Brown*2
Tandoori Roast Chicken
'''
deck0 = Deck.from_str(deck_string)
deck1 = Deck.from_str(deck_string)
match = Match()
match.set_deck([deck0, deck1])
match.start()
match.step()

agent_0 = RandomAgent(player_idx = 0)
agent_1 = RandomAgent(player_idx = 1)

while not match.is_game_end():
    if match.need_respond(0):
        match.respond(agent_0.generate_response(match))
    elif match.need_respond(1):
        match.respond(agent_1.generate_response(match))
    match.step()

print(f'winner is {match.winner}')
```

### Customize cards and characters

To customize cards and characters, you need to understand the actions,
event handlers and value modifiers. All interaction are done by actions, and
all actions are triggered by events. Value modifiers are for modifying values
such as dice cost and damage. The easiest way to implement a new object is to
copy an existing card/character/skill/status... and modify it. 

`templates/character.py` is a template for characters. You can copy it
and modify it to implement a new character. You can define any object that is
related to the character, e.g. skills, talents, summons, status. Then, you 
should create the description for these objects, which is used in the frontend,
and class registry will reject objects without description. Finally, register
all objects as well as their descriptions to class registry with 
`register_class` function. Note the template uses relative imports, as it is
used for creating new official characters. You need to change them to absolute
imports if you want to create a new character outside this project.

Define a new card is relatively simple, you can refer to `templates/card.py`,
it defined a new card "Big Strategize" which costs 2 any dice and draws 3 
cards. As a sample of custom card, it uses absolute import, so you can use it
outside this project.

You can manually register new objects and use them in the match.
Take "Big Strategize" for example, install `lpsim` first, then type
`import templates.card` after `import lpsim`. Then you can create a HTTP
server by `a = HTTPServer(); a.run()` to see that a new card is added to the 
candidate card list.

## Details

Pydantic to save & load states of match, exported data is complete to restore
from certain state and continue running, and also easy for frontend to render
the game states.

High compatible with different version of characters or cards. You can start a
match between version 3.8 Itto-Barbara-Noelle and version 3.3 dual-Geo Maguu 
Kenki.

Interact by request and response. When request list is not empty, agents need
to response to one of the request. When multiple players need to response,
(e.g. switch card and choose character at startup),
their requests will be generated simultaneously.

All modifications to the match table are orchestrated through actions. 
Each action triggers an event and has the potential to activate subsequent 
actions. These newly activated actions are appended to the top of the existing 
action list, akin to a stacked-lists structure. Refer to definition of 
`EventFrame`.

Objects integrated into this system introduce two types of triggers: event 
handlers and value modifiers. Event handlers function to monitor events and 
produce lists of actions in response. Value modifiers is used on edit 
mutable values and updating internal states if is necessary. Modifiable values
applies to attributes like initial dice color, damage, and cost.

All codes are tested with pytest and 100% coverage (except defensive codes,
which are marked with `# pragma: no cover`). With the support of different
version compatibility, when a new version is implemented, all past tests
should be passed without modification.

## Contribution

Contributions are welcomed, however, currently there is no detailed documentation. 
Before contributing, you can read [CONTRIBUTING.md](CONTRIBUTING.md),
which contains information on how to install the development environment and
how to run tests.

To add new character related objects (Character, Skill, Talent,
Summon, Status), please refer to `templates/character.py` and implemented
characters.
To add a new card, please refer to existing card implementations in 
`server/card`.
After coding, use `register_class` function to register new objects to the
simulator, and you can use them in the match.

Developing this project takes the author a lot of time (which should be used to 
play GITCG and Simulated Universe). If you think this project is helpful, you
can support the author by WeChat.

<p align="center">
    <img src="docs/images/wechat.png" alt="wechat" width="150">
</p>
