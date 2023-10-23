from src.lpsim.network import HTTPServer
from src.lpsim.server.match import MatchConfig


if __name__ == '__main__':
    deck_str_1 = '''
    charactor:Fischl@3.3
    charactor:Rhodeia of Loch@3.3
    charactor:Fatui Pyro Agent@3.3
    Tubby@3.3
    Sumeru City@3.7
    Lucky Dog's Silver Circlet@3.3
    Strategize@3.3
    Leave It to Me!@3.3
    Paid in Full@3.3
    Sangonomiya Shrine@3.7
    Lotus Flower Crisp@3.3
    Mushroom Pizza@3.3
    Favonius Cathedral@3.3
    Mushroom Pizza@3.3
    Magic Guide@3.3*19
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
        decks = [deck_str_1, deck_str_2],
        match_config = MatchConfig(
            check_deck_restriction = False,
            card_number = None,
            max_same_card_number = None,
            charactor_number = None,
            max_round_number = 999,
            # max_hand_size = 999,
            # recreate_mode = True,
            history_level = 10,
            make_skill_prediction = True,
            random_object_information = {
                'rhodeia': [
                    'squirrel', 'raptor', 'frog', 'squirrel', 'raptor', 'frog',
                    'frog', 'squirrel', 'squirrel'
                ],
            }
        )
    )
    server.run()
