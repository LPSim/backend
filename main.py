import logging
from typing import Literal
from server.match import Match
from utils import BaseModel
from server.deck import Deck
from agents.nothing_agent import NothingAgent
from agents.random_agent import RandomAgent
from agents.agent_base import AgentBase


class Main(BaseModel):
    """
    """

    version: str = '1.0.0'
    name: Literal['GITCG'] = 'GITCG'
    match: Match = Match()


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = RandomAgent(player_id = 1)
    main = Main()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMob',
                'element': 'DENDRO',
            },
            {
                'name': 'HydroMob',
                'element': 'HYDRO',
            },
            {
                'name': 'PhysicalMob',
                'element': 'PYRO',
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    main.match.set_deck([deck, deck])
    main.match.match_config.max_same_card_number = 30
    assert main.match.start()
    main.match.step()  # switch card

    def make_respond(agent: AgentBase, main: Main):
        while True:
            resp = agent.generate_response(main.match)
            if resp is None:
                break
            main.match.respond(resp)
            if len(main.match.requests) == 0:
                main.match.step()

    while main.match.round_number < 2:
        make_respond(agent_0, main)
        make_respond(agent_1, main)
    mainjson = main.json()
    # # switch 3 cards
    # main.match.respond(SwitchCardResponse(
    #     request = main.match.requests[0], card_ids = [3, 1, 2]))
    # main.match.step()
    # make_respond(agent_0, main)
    # # choose charactor
    # main.match.respond(ChooseCharactorResponse(
    #     request = main.match.requests[0], charactor_id = 1
    # ))
    # main.match.step()
    # make_respond(agent_0, main)
    # # reroll dice not dendro or omni
    # main.match.respond(RerollDiceResponse(
    #     request = main.match.requests[0],
    #     reroll_dice_ids = [
    #         x for x in range(8) 
    #         if main.match.requests[0].colors[x] not in (
    #             DieColor.DENDRO, DieColor.OMNI
    #         )
    #     ]
    # ))
    # main.match.step()  # on action request
    # make_respond(agent_0, main)
    # current_player = main.match.current_player
    # while True:
    #     # do elemental tuning until no card or no available dice
    #     req_names = [x.name for x in main.match.requests]
    #     if 'ElementalTuningRequest' not in req_names:
    #         break
    #     idx = req_names.index('ElementalTuningRequest')
    #     assert current_player == main.match.requests[idx].player_id
    #     main.match.respond(ElementalTuningResponse(
    #         request = main.match.requests[idx],
    #         die_color = main.match.requests[idx].dice_colors[0],
    #         card_id = random.choice(main.match.requests[idx].card_ids)
    #     ))
    #     main.match.step()
    # # switch charactor
    # assert main.match.current_player == current_player
    # main.match.respond(SwitchCharactorResponse(
    #     request = main.match.requests[0],
    #     charactor_id = 2,
    #     cost_ids = [0],
    # ))
    # main.match.step()
    # make_respond(agent_0, main)
    # # switch charactor 7 times and should run out of dice
    # for i in range(7):
    #     assert main.match.current_player == current_player
    #     main.match.respond(SwitchCharactorResponse(
    #         request = main.match.requests[0],
    #         charactor_id = i % 2,
    #         cost_ids = [0],
    #     ))
    #     main.match.step()
    # # declare round end
    # assert len(main.match.requests) == 1
    # main.match.respond(DeclareRoundEndResponse(
    #     request = main.match.requests[0],
    # ))
    # main.match.step()
    # # next round the other player should be first
    # assert main.match.current_player == 1 - current_player
    # mainjson = (main.json())
