import pytest
from lpsim.env.utils import cost_default_selector, get_color_order
from lpsim.server.consts import DieColor
from lpsim.server.deck import Deck
from lpsim.server.match import Match
from lpsim.server.struct import Cost


mo_ying_cao_4_5 = "2BPTnM7QxlTU+xjW2EMTuFrSzSQEy/PT1kTE/vbWznQDD4TTz2TUzvnT1nQj1JjU0PPD"
lin_ma_long_4_5 = "4+Izp+vf5iPzG/zm5GJyq2nf5WPTCgLl5VLjrQXh5RMC2pvi3lNiDZzl3oNyHqPm35LS"
san_jian_li_4_5 = "AxGR9DsQAzEx9X0QCEHB9pgQCmFx96UQC5FB+r4RDiLRA+gRD1JxBukRD6KBDPIRELEB"
code1 = """
oooooooo
GEO 3 1 0
[] []
[OMNI] [7]
[OMNI] [7]
oooooooo    
GEO 3 1 0
[] []
[OMNI] [7]
[OMNI] [7]
oooooooo
GEO 0 3 0
[] []
[OMNI] [7]
[OMNI, OMNI, OMNI] [7, 6, 5]
oooooooo  
GEO 3 0 0   
[] []
[OMNI] [7]
[OMNI, OMNI, OMNI] [7, 6, 5]
oooooooo 
GEO 0 3 1
[] []
[OMNI] [7]
[OMNI, OMNI, OMNI] [7, 6, 5]
oooooooo  
GEO 3 0 1
[] []
[OMNI] [7]
[OMNI, OMNI, OMNI, OMNI] [7, 6, 5, 4]
oooggdd
GEO 0 3 0
[GEO, GEO] [3, 4]
[GEO] [4]
[GEO, GEO, OMNI] [4, 3, 2]
ooohhdd   
GEO 0 3 0
[] []
[DENDRO] [6]
[DENDRO, DENDRO, OMNI] [6, 5, 2]
oooggdd   
GEO 3 0 1
[GEO, GEO] [3, 4]
[GEO] [4]
[GEO, GEO, OMNI, DENDRO] [4, 3, 2, 6]
oooppdd   
GEO 3 0 1
[PYRO, PYRO] [3, 4]
[PYRO] [4]
[OMNI, OMNI, OMNI, PYRO] [2, 1, 0, 4]
oooppdd
GEO 0 3 0
[PYRO, PYRO] [3, 4]
[PYRO] [4]
[PYRO, PYRO, OMNI] [4, 3, 2]
oooddhh   
GEO 0 3 0
[] []
[DENDRO] [4]
[DENDRO, DENDRO, OMNI] [4, 3, 2]
ooohhgd
GEO 0 3 0
[GEO] [5]
[GEO] [5]
[HYDRO, HYDRO, OMNI] [4, 3, 2]
oopghd 
GEO 0 3 0
[PYRO, GEO] [2, 3]
[GEO] [3]
[GEO, OMNI, OMNI] [3, 1, 0]
oopghd    
DENDRO 3 0 2
[PYRO, GEO] [2, 3]
[GEO] [3]
[DENDRO, OMNI, OMNI, GEO, PYRO] [5, 1, 0, 3, 2]
oopghd       
DENDRO 2 0 3
[PYRO, GEO] [2, 3]
[GEO] [3]
[DENDRO, OMNI, GEO, PYRO, HYDRO] [5, 1, 3, 2, 4]
"""
code2 = """
ccceee
GEO 0 3 0
[] []
[ELECTRO] [5]
[ELECTRO, ELECTRO, ELECTRO] [5, 4, 3]
ccc
GEO 0 3 0
[] []
[CRYO] [2]
[CRYO, CRYO, CRYO] [2, 1, 0]
"""
code3 = """
ccceee
GEO 0 3 0
[CRYO, CRYO, CRYO] [0, 1, 2]
[CRYO] [2]
[CRYO, CRYO, CRYO] [2, 1, 0]
"""


def dice_selection_func(
    code_str: str,
    deck_str_1: str,
    deck_str_2: str,
    kill01: bool,
    active: int,
):
    code = [x.strip() for x in code_str.strip().split("\n")]
    code = [code[i : i + 5] for i in range(0, len(code), 5)]

    m = Match()
    decks = [Deck.from_deck_code(deck_str_1), Deck.from_deck_code(deck_str_2)]
    m.set_deck(decks)
    assert m.start()[0]

    m.player_tables[0].active_character_idx = active
    if kill01:
        m.player_tables[0].characters[1].hp = 0
        m.player_tables[0].characters[1].is_alive = False

    def getd(dstr):
        dm = {
            "c": DieColor.CRYO,
            "h": DieColor.HYDRO,
            "p": DieColor.PYRO,
            "e": DieColor.ELECTRO,
            "g": DieColor.GEO,
            "d": DieColor.DENDRO,
            "a": DieColor.ANEMO,
            "o": DieColor.OMNI,
        }
        return [dm[c] for c in dstr]

    for s, s2, res1, res2, res3 in code:
        colors = getd(s)
        m.player_tables[0].dice.colors = getd(s)
        s2 = s2.split(" ")
        cost = Cost(
            elemental_dice_color=DieColor(s2[0]),
            elemental_dice_number=int(s2[1]),
            same_dice_number=int(s2[2]),
            any_dice_number=int(s2[3]),
        )
        selected = cost_default_selector(m, 0, "reroll", cost)
        assert res1 == f"{[colors[x] for x in selected]} {selected}"
        selected = cost_default_selector(m, 0, "tune", cost)
        assert res2 == f"{[colors[x] for x in selected]} {selected}"
        selected = cost_default_selector(m, 0, "cost", cost)
        assert res3 == f"{[colors[x] for x in selected]} {selected}"
    return m


def test_dice_selection():
    dice_selection_func(code1, mo_ying_cao_4_5, lin_ma_long_4_5, False, -1)


def test_dice_selection_2():
    match1 = dice_selection_func(code2, san_jian_li_4_5, mo_ying_cao_4_5, False, 1)
    match2 = dice_selection_func(code3, san_jian_li_4_5, mo_ying_cao_4_5, True, 0)
    match1.player_tables[0].dice.colors = [
        DieColor.DENDRO,
        DieColor.ELECTRO,
        DieColor.OMNI,
        DieColor.GEO,
        DieColor.CRYO,
        DieColor.HYDRO,
        DieColor.OMNI,
    ]
    res = get_color_order(match1.player_tables[0], True)
    assert f"{res[0]}" == "[OMNI, ANEMO, CRYO, ELECTRO, HYDRO, PYRO, GEO, DENDRO]"
    assert res[1] == [
        "omni",
        "active",
        "active",
        "standby",
        "other",
        "other",
        "other",
        "other",
    ]
    match2.player_tables[0].dice.colors = [
        DieColor.DENDRO,
        DieColor.ELECTRO,
        DieColor.OMNI,
        DieColor.GEO,
        DieColor.CRYO,
        DieColor.HYDRO,
        DieColor.OMNI,
    ]
    res = get_color_order(match2.player_tables[0], True)
    assert f"{res[0]}" == "[OMNI, ANEMO, ELECTRO, CRYO, HYDRO, PYRO, GEO, DENDRO]"
    assert res[1] == [
        "omni",
        "active",
        "standby",
        "other",
        "other",
        "other",
        "other",
        "other",
    ]
    match2.player_tables[0].dice.colors = [DieColor.ANEMO]
    with pytest.raises(ValueError):
        cost_default_selector(
            match2,
            0,
            "cost",
            Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=1),
        )


if __name__ == "__main__":
    test_dice_selection()
    test_dice_selection_2()
