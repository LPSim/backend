import logging
from typing import Literal
from src.lpsim.server.match import Match
from src.lpsim.utils import BaseModel
from src.lpsim.server.deck import Deck
from src.lpsim.agents import RandomAgent
from src.lpsim.model.model import model


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    agent_0 = RandomAgent(player_idx=0)
    agent_1 = RandomAgent(player_idx=1)
    match = Match()
    deck = Deck.from_str(
        """
        default_version:4.4
        character:Lyney
        character:Millennial Pearl Seahorse
        character:Azhdaha
        Gambler's Earrings
        Gambler's Earrings
        Gilded Dreams
        Gilded Dreams
        Flowing Rings
        Heart of Khvarena's Brilliance
        Heart of Khvarena's Brilliance
        Liben
        Liben
        Chang the Ninth
        Chang the Ninth
        Dunyarzad
        Dunyarzad
        Jeht
        Jeht
        Treasure-Seeking Seelie
        Treasure-Seeking Seelie
        Seed Dispensary
        Seed Dispensary
        Memento Lens
        Covenant of Rock
        Strategize
        Strategize
        I Haven't Lost Yet!
        Lyresong
        Lyresong
        The Boar Princess
        The Boar Princess
        Sunyata Flower
        Sunyata Flower
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.history_level = 10
    match.config.check_deck_restriction = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
    match.config.card_number = None
    assert match.start()[0]
    match.step()

    while match.round_number < 50 and not match.is_game_end():
        if match.need_respond(0):
            current_agent = agent_0
        elif match.need_respond(1):
            current_agent = agent_1
        else:
            raise RuntimeError("no agent need to respond")
        resp = current_agent.generate_response(match)
        print(resp)
        assert resp is not None
        match.respond(resp)
        match.step()

    model = model()
    model.match_to_json(match, "Jeht")
