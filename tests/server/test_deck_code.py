import pytest
from src.lpsim.utils import deck_code_to_deck_str, deck_str_to_deck_code
from src.lpsim import Deck


def test_deck_code():
    deck_str = '''
    # nahida mona fischl, with 4.0 wind and freedom
    default_version:4.1
    charactor:Fischl@3.3
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
    Calx's Arts*2
    Adeptus' Temptation*2
    Lotus Flower Crisp*2
    Mondstadt Hash Brown*2
    Tandoori Roast Chicken
    '''
    deck_str_over_1 = deck_str + 'charactor:Beidou'
    deck_str_over_2 = deck_str + 'Strategize'
    deck_str_miss_1 = deck_str.replace('charactor:Mona', '')
    deck_str_miss_2 = deck_str.replace('Tanodoori Roast Chicken', '')
    deck_str_over_3 = deck_str.replace('charactor:Mona', 'charactor:Mona*2')
    # check deck str to deck code
    deck_code = deck_str_to_deck_code(deck_str)
    with pytest.raises(ValueError):
        deck_str_to_deck_code(deck_str_over_1)
    with pytest.raises(ValueError):
        deck_str_to_deck_code(deck_str_over_2)
    with pytest.raises(ValueError):
        deck_str_to_deck_code(deck_str_over_3)
    deck_code_miss_1 = deck_str_to_deck_code(deck_str_miss_1)
    deck_code_miss_2 = deck_str_to_deck_code(deck_str_miss_2)

    # if retry time is small, will fail.
    with pytest.raises(ValueError):
        for i in range(10000):  # pragma: no branch
            # it is nearly impossible to generate a legal deck code 10000 times
            deck_str_to_deck_code(deck_str, max_retry_time = 1)

    # check deck code to deck str is same
    def check_deck_str_same(str1: str, str2: str) -> bool:
        """
        Will use str to generate deck, and parse names, and sort to confirm
        whether they are same.
        """
        deck1 = Deck.from_str(str1)
        deck2 = Deck.from_str(str2)
        ch_names1 = sorted([x.name for x in deck1.charactors])
        ca_names1 = sorted([x.name for x in deck1.cards])
        ch_names2 = sorted([x.name for x in deck2.charactors])
        ca_names2 = sorted([x.name for x in deck2.cards])
        return ch_names1 == ch_names2 and ca_names1 == ca_names2

    for _ in range(100):
        deck_str_rev = deck_code_to_deck_str(deck_code)
        deck_str_miss_1_rev = deck_code_to_deck_str(deck_code_miss_1)
        deck_str_miss_2_rev = deck_code_to_deck_str(deck_code_miss_2)
        # revert result should same
        assert check_deck_str_same(deck_str, deck_str_rev)
        assert check_deck_str_same(deck_str_miss_1, deck_str_miss_1_rev)
        assert check_deck_str_same(deck_str_miss_2, deck_str_miss_2_rev)
        # generate new deck code
        deck_code = deck_str_to_deck_code(deck_str)
        deck_code_miss_1 = deck_str_to_deck_code(deck_str_miss_1)
        deck_code_miss_2 = deck_str_to_deck_code(deck_str_miss_2)

    # when version hint is added, output should contain version
    deck_str_rev_version = deck_code_to_deck_str(deck_code, version = '4.0')
    assert 'default_version:4.0' in deck_str_rev_version

    deck_instance = Deck.from_deck_code(deck_code)
    deck_code_rev = deck_instance.to_deck_code()
    assert check_deck_str_same(deck_str, deck_code_to_deck_str(deck_code_rev))


if __name__ == "__main__":
    test_deck_code()
