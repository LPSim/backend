import logging
from typing import Literal
from server.match import Match
from utils import BaseModel
from server.deck import Deck
from agents import NothingAgent
from agents import RandomAgent


class Main(BaseModel):
    """
    """

    version: str = '1.0.0'
    name: Literal['GITCG'] = 'GITCG'
    match: Match = Match()


if __name__ == '__main__':
    logging.basicConfig(level = logging.WARNING)
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = RandomAgent(player_id = 1)
    main = Main()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
            },
            {
                'name': 'HydroMob',
            },
            {
                'name': 'ElectroMobMage',
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
    main.match.enable_history = True
    assert main.match.start()
    main.match.step()

    while main.match.round_number < 100 and not main.match.is_game_end():
        if main.match.need_respond(0):
            current_agent = agent_0
        elif main.match.need_respond(1):
            current_agent = agent_1
        else:
            raise RuntimeError('no agent need to respond')
        resp = current_agent.generate_response(main.match)
        assert resp is not None
        main.match.respond(resp)
        main.match.step()

    main.match.get_history_json(filename = 'logs.txt')
    print('game end, save to logs.txt')
