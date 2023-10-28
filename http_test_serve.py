from src.lpsim.server.event_handler import OmnipotentGuideEventHandler
from src.lpsim.network import HTTPServer
from src.lpsim.server.match import MatchConfig, Match
from tests.utils_for_test import get_random_state
import logging


logging.basicConfig(level = logging.INFO)


if __name__ == '__main__':
    deck_str_1 = '''
        default_version:4.1
        charactor:Noelle
        charactor:Mona
        charactor:Dehya
        # Gales of Reverie*10
        # Beneficent*10
        Stalwart and True*10
        Sweet Madame*10
    '''
    deck_str_2 = '''
    charactor:Nahida@3.7
    charactor:Rhodeia of Loch@3.3
    charactor:Fischl@3.3
    Gambler's Earrings@3.8
    Paimon@3.3
    Chef Mao@4.1
    Dunyarzad@4.1
    The Bestest Travel Companion!@3.3
    Paimon@3.3
    Liben@3.3
    Liben@3.3
    Send Off@3.7
    Teyvat Fried Egg@4.1
    Dunyarzad@4.1
    Sweet Madame@3.3
    I Haven't Lost Yet!@4.0
    Send Off@3.7
    Lotus Flower Crisp@3.3
    Magic Guide@3.3*15
    '''
    server = HTTPServer(
        decks = [deck_str_1, deck_str_1],
        match_config = MatchConfig(
            check_deck_restriction = False,
            card_number = None,
            max_same_card_number = None,
            charactor_number = None,
            max_round_number = 999,
            random_first_player = False,
            # max_hand_size = 999,
            # recreate_mode = True,
            history_level = 10,
            # make_skill_prediction = True,
            # random_object_information = {
            #     'rhodeia': [
            #         'squirrel', 'raptor', 'frog', 'squirrel', 'raptor', 
            #         'frog', 'frog', 'squirrel', 'squirrel'
            #     ],
            # }
        )
    )

    # fix random seed
    match = Match(random_state = get_random_state())
    match.set_deck(server.decks)
    match.config = server.match.config

    # rich mode
    match.event_handlers.append(OmnipotentGuideEventHandler())
    match.config.initial_dice_number = 16

    server.match = match
    server.match.start()
    server.match._save_history()
    server.match.step()
    server.run()
