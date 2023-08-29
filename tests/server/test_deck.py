from server.deck import Deck
from tests.utils_for_test import remove_ids


def test_deck_string():
    deck_dict_1 = Deck(**{
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    })
    deck_str_1 = Deck.from_str('''
        charactor:DendroMobMage*2
        charactor:ElectroMobMage
        Strategize*30
    ''')
    deck_dict_1 = remove_ids(deck_dict_1)
    deck_str_1 = remove_ids(deck_str_1)
    assert deck_str_1 == deck_dict_1
    deck_dict_2 = Deck(**{
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Wine-Stained Tricorne',
            }
        ] * 10 + [
            {
                'name': 'Laurel Coronet',
            }
        ] * 10 + [
            {
                'name': 'Strategize',
            }
        ] * 10,
    })
    deck_str_2 = Deck.from_str('''
        charactor:DendroMobMage*2
        charactor:ElectroMobMage
        Wine-Stained Tricorne*10
        Laurel Coronet*10
        Strategize*10
    ''')
    deck_dict_2 = remove_ids(deck_dict_2)
    deck_str_2 = remove_ids(deck_str_2)
    assert deck_str_2 == deck_dict_2
    deck_dict_3 = Deck(**{
        'name': 'Deck',
        'charactors': [
            {
                'name': 'Fischl',
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'PyroMobMage',
                'element': 'PYRO',
            },
        ],
        'cards': [
            {
                'name': 'Stellar Predator',
            }
        ] * 30,
    })
    deck_str_3 = Deck.from_str('''
        charactor:Fischl
        charactor:DendroMobMage
        charactor:PyroMobMage
        Stellar Predator*30
    ''')
    deck_dict_3 = remove_ids(deck_dict_3)
    deck_str_3 = remove_ids(deck_str_3)
    assert deck_str_3 == deck_dict_3


def test_deck_assertions():
    deck = Deck.from_str('''
        charactor:DendroMobMage*2
        charactor:ElectroMobMage
        Strategize*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None
    )
    assert deck.check_legal(
        card_number = 30, 
        max_same_card_number = 30,
        charactor_number = 3
    )
    assert not deck.check_legal(
        card_number = 29, 
        max_same_card_number = 30,
        charactor_number = 3
    )
    assert not deck.check_legal(
        card_number = 31, 
        max_same_card_number = 30,
        charactor_number = 3
    )
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 29,
        charactor_number = 3
    )
    assert deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 3
    )
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 2
    )
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 4
    )


if __name__ == '__main__':
    test_deck_string()
