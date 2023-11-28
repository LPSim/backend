from src.lpsim.server.deck import Deck
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
        'default_version': '4.0',
    })
    deck_str_1 = Deck.from_str('''
        default_version:4.0
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
        'default_version': '4.0',
    })
    deck_str_2 = Deck.from_str('''
        default_version:4.0

        # charactors
        charactor:DendroMobMage*2
        charactor:ElectroMobMage

        # cards
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
        'default_version': '4.0',
    })
    deck_str_3 = Deck.from_str('''
        default_version:4.0
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
        default_version:4.0
        charactor:DendroMobMage*2
        charactor:ElectroMobMage
        Strategize*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False
    )[0]
    assert deck.check_legal(
        card_number = 30, 
        max_same_card_number = 30,
        charactor_number = 3,
        check_restriction = False
    )[0]
    assert not deck.check_legal(
        card_number = 29, 
        max_same_card_number = 30,
        charactor_number = 3,
        check_restriction = False
    )[0]
    assert not deck.check_legal(
        card_number = 31, 
        max_same_card_number = 30,
        charactor_number = 3,
        check_restriction = False
    )[0]
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 29,
        charactor_number = 3,
        check_restriction = False
    )[0]
    assert deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 3,
        check_restriction = False
    )[0]
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 2,
        check_restriction = False
    )[0]
    assert not deck.check_legal(
        card_number = 30, 
        max_same_card_number = 31,
        charactor_number = 4,
        check_restriction = False
    )[0]


def test_deck_restriction():
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Collei
        charactor:Barbara
        Wind and Freedom*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert not deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        Wind and Freedom*30
        Sweet Madame*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        Elemental Resonance: Woven Waters*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        Elemental Resonance: Woven Weeds*30
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert not deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        The Seed of Stored Knowledge*5
        Prophecy of Submersion*5
        Glorious Season*5
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        The Seed of Stored Knowledge*5
        Prophecy of Submersion*5
        Grand Expectation*5
    ''')
    assert deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = False,
    )[0]
    assert not deck.check_legal(
        card_number = None, 
        max_same_card_number = None,
        charactor_number = None,
        check_restriction = True,
    )[0]


def test_deck_to_str_to_deck():
    deck = Deck.from_str('''
        default_version:4.0
        charactor:Nahida
        charactor:Mona
        charactor:Barbara
        The Seed of Stored Knowledge*5
        Prophecy of Submersion*5
        Grand Expectation*5
    ''')
    deck2 = Deck.from_str(deck.to_str())
    assert remove_ids(deck) == remove_ids(deck2)


if __name__ == '__main__':
    test_deck_string()
    test_deck_restriction()
    test_deck_to_str_to_deck()
