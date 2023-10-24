# Lochfolk Prinzessin Simulator (LPSim): A Genius Invokation TCG Simulator

---

[![Coverage Status](https://coveralls.io/repos/github/LPSim/backend/badge.svg?branch=master)](https://coveralls.io/github/LPSim/backend?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/lpsim.svg?style=flat-square&color=blue)](https://pypi.org/project/lpsim/)

Backend of Lochfolk Prinzessin Simulator, which simulates Genius Invokation 
TCG, written with Python 3.10 using Pydantic and FastAPI.

This project is under AGPL-3.0 license.

## Progress

All charactors and cards with their balance changes until 4.1 are done.

## Feature

- All charactors and cards until 4.1 are implemented.
- Support using different version of charactors and cards in a same deck.
- Support serve as a mini server to interact with the match.
- A frontend is provided to interact with the server.
- Consistent when load from a state and continue running.
- 100% Coverage of codes.

## Usage

This project works with Python 3.10 or newer.

### Installation by pip

To install the newest release version, use `pip install lpsim`. You can find
the newest release version on [PyPI](https://pypi.org/project/lpsim/), and
you can find the change log on [CHANGELOG.md](CHANGELOG.md).

To install the newest development version, use 
`pip install lpsim -i https://test.pypi.org/simple/`. When new commits are
pushed to `master` branch and pass all tests, a new version will be released 
on test PyPI.

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
from anywhere. When initialize HTTPServer, you can set decks and match configs
to create a match with specified rules.

To start the match, open a 
[frontend web page](https://lpsim.zyr17.cn/index.html), change server
URL on top right (default is `http://localhost:8000`), and follow the 
instructions on the page to set Deck and start match between two players.

Currently exception
management is chaos, errors may set game state to ERROR, raise Exception on
server side, make empty response on agent, return 404/500, or run JS failed on
frontend. Please open console of frontend and check the error message on both
sides.

### Start a match non-interactively

#### Define the deck

To start a match, you should firstly 
define decks for both players. Supports text-based or json-based deck 
definition. Usually, `Deck.from_str` is enough to define a deck, which contains
charactors and cards definition, and can control their versions. The deck 
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
   If error occured (e.g. deck is not valid), it will print error message and
   return False.
5. Progress through the match by employing the `Match.step` function. 
   By default, the step function will continually execute until the match 
   either ends or generates requests requiring responses, or the match ends.

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
charactor:Fischl
charactor:Mona
charactor:Nahida
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
Clax's Arts*2
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

## Details

Pydantic to save & load states of match, exported data is complete to restore
from certain state and continue running, and also easy for frontend to render
the game states.

High compatible with different version of charactors or cards. (Although
currently not implemented,) You can start a match between version 3.8 
Itto-Barbara-Noelle and version 3.3 dual-Geo Maguu Kenki.

Interact by request and response. When request list is not empty, agents need
to response to one of the request. When multiple players need to response,
(e.g. switch card and choose charactor at startup),
their requests will be generated simultaneously.

All modifications to the match table are orchestrated through actions. 
Each action triggers an event and has the potential to activate subsequent 
actions. These newly activated actions are appended to the top of the existing 
action list, akin to a stacked-lists structure.

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

Contributions are welcomed, however, currently there is no detailed guide for
contribution. To add new charactor related objects (Charactor, Skill, Talent,
Summon, Status), please refer to `server/charactor/template.py` and implemented
charactors.
To add a new card, please refer to existing card implementations in 
`server/card`.
