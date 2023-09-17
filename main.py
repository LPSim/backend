import logging
from typing import Literal
from src.lpsim.server.match import Match
from src.lpsim.utils import BaseModel
from src.lpsim.server.deck import Deck
from src.lpsim.agents import NothingAgent
from src.lpsim.agents import RandomAgent


class Main(BaseModel):
    """
    """

    version: str = '1.0.0'
    name: Literal['GITCG'] = 'GITCG'
    match: Match = Match()


if __name__ == '__main__':
    logging.basicConfig(level = logging.WARNING)
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = RandomAgent(player_idx = 1)
    main = Main()
    deck = Deck.from_str(
        '''
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        '''
    )
    main.match.set_deck([deck, deck])
    main.match.config.max_same_card_number = 30
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
