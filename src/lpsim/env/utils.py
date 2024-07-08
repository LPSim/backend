from typing import Literal
from lpsim.server.character.character_base import CharacterBase
from lpsim.server.consts import ELEMENT_DEFAULT_ORDER, ELEMENT_TO_DIE_COLOR, DieColor
from lpsim.server.deck import Deck
from lpsim.server.match import Match
from lpsim.server.player_table import PlayerTable
from lpsim.server.struct import Cost


def get_color_order(
    table: PlayerTable, return_type: bool = False
) -> (
    list[DieColor]
    | tuple[list[DieColor], list[Literal["omni", "active", "standby", "other"]]]
):
    """
    give color order, and optionally color types based on table.
    """
    ret_c: list[DieColor] = [DieColor.OMNI]
    ret_t: list[Literal["omni", "active", "standby", "other"]] = ["omni"]
    characters: list[CharacterBase] = []
    if table.active_character_idx != -1:
        characters.append(table.characters[table.active_character_idx])
    characters += table.characters
    for c in characters:
        if c.is_alive:
            t = "standby"
            if c.position.character_idx == table.active_character_idx:
                t = "active"
            dc = ELEMENT_TO_DIE_COLOR[c.element]
            if dc not in ret_c:
                ret_c.append(dc)
                ret_t.append(t)
            if c.name == "Maguu Kenki" and DieColor.CRYO not in ret_c:
                ret_c.append(DieColor.CRYO)
                ret_t.append(t)
    for c in ELEMENT_DEFAULT_ORDER:
        c = ELEMENT_TO_DIE_COLOR[c]
        if c not in ret_c:
            ret_c.append(c)
            ret_t.append("other")
    if return_type:
        return ret_c, ret_t
    else:
        return ret_c


def sort_dice(
    table: PlayerTable, dice_list: list[DieColor]
) -> list[tuple[DieColor, int]]:
    order: list[DieColor] = get_color_order(table)  # type: ignore
    combined = [(d, didx) for didx, d in enumerate(dice_list)]
    combined.sort(key=lambda x: order.index(x[0]) * 1024 + x[1])
    return combined


def cost_default_selector(
    match: Match,
    player_idx: int,
    mode: Literal["reroll", "tune", "cost"],
    cost: Cost | None = None,
) -> list[int]:
    table = match.player_tables[player_idx]
    dice_list = table.dice.colors
    sorted_colors = sort_dice(table, dice_list)

    if mode == "reroll":
        # reroll-dice will be any. select dice that color not right
        c_colors = [DieColor.OMNI]
        for character in table.characters:
            if not character.is_alive:
                continue
            c_colors.append(ELEMENT_TO_DIE_COLOR[character.element])
            if character.name == "Maguu Kenki":
                c_colors.append(DieColor.CRYO)
        selected = []
        for idx, color in enumerate(dice_list):
            if color not in c_colors:
                selected.append(idx)
        return selected
    elif mode == "tune":
        # click last
        return [sorted_colors[-1][1]]

    selected: list[int] = []
    assert cost is not None, "Must have cost when mode is cost"
    if cost.same_dice_number > 0:
        omni_count = 99999
        done: set[DieColor] = set()
        for cid in range(len(sorted_colors) - 1, -1, -1):
            # back to front, one color one chance. keep less omni one.
            color = sorted_colors[cid][0]
            if color in done:
                continue
            done.add(color)
            now_selected: list[int] = []
            now_omni_count = 0
            for did in range(cid, -1, -1):
                if sorted_colors[did][0] == DieColor.OMNI:
                    now_omni_count += 1
                    now_selected.append(sorted_colors[did][1])
                elif sorted_colors[did][0] == color:
                    now_selected.append(sorted_colors[did][1])
            if len(now_selected) < cost.same_dice_number:
                continue
            now_same_count = len(now_selected) - now_omni_count
            if color != DieColor.OMNI:
                now_omni_count = max(0, cost.same_dice_number - now_same_count)
            if now_omni_count > omni_count:
                continue
            if now_omni_count < omni_count:
                selected = now_selected[: cost.same_dice_number]
                omni_count = now_omni_count
                continue
        return selected

    # firstly select element
    for cid in range(len(sorted_colors) - 1, -1, -1):
        if len(selected) == cost.elemental_dice_number:
            break
        color = sorted_colors[cid][0]
        if color == cost.elemental_dice_color or color == DieColor.OMNI:
            selected.append(sorted_colors[cid][1])
    # then select any
    for cid in range(len(sorted_colors) - 1, -1, -1):
        if len(selected) == cost.any_dice_number + cost.elemental_dice_number:
            break
        if sorted_colors[cid][1] not in selected:
            selected.append(sorted_colors[cid][1])
    return selected


if __name__ == "__main__":
    m = Match()
    mo_ying_cao_4_5 = (
        "2BPTnM7QxlTU+xjW2EMTuFrSzSQEy/PT1kTE/vbWznQDD4TTz2TUzvnT1nQj1JjU0PPD"
    )
    lin_ma_long_4_5 = (
        "4+Izp+vf5iPzG/zm5GJyq2nf5WPTCgLl5VLjrQXh5RMC2pvi3lNiDZzl3oNyHqPm35LS"
    )
    decks = [Deck.from_deck_code(mo_ying_cao_4_5), Deck.from_deck_code(lin_ma_long_4_5)]
    m.set_deck(decks)
    assert m.start()[0]

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

    while True:
        s = input().strip()
        colors = getd(s)
        m.player_tables[0].dice.colors = getd(s)
        s2 = input().strip().split()
        cost = Cost(
            elemental_dice_color=DieColor(s2[0]),
            elemental_dice_number=int(s2[1]),
            same_dice_number=int(s2[2]),
            any_dice_number=int(s2[3]),
        )
        selected = cost_default_selector(m, 0, "reroll", cost)
        print([colors[x] for x in selected], selected)
        selected = cost_default_selector(m, 0, "tune", cost)
        print([colors[x] for x in selected], selected)
        selected = cost_default_selector(m, 0, "cost", cost)
        print([colors[x] for x in selected], selected)


"""
oooooooo
GEO 3 1 0 1
[] []
[OMNI] [7]
[OMNI] [7]
oooooooo    
GEO 3 1 0 0
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
