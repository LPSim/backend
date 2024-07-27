from typing import Literal
from lpsim.server.character.character_base import CharacterBase
from lpsim.server.consts import ELEMENT_DEFAULT_ORDER, ELEMENT_TO_DIE_COLOR, DieColor
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
    if cost.elemental_dice_number > 0:
        for cid in range(len(sorted_colors) - 1, -1, -1):
            color = sorted_colors[cid][0]
            if color == cost.elemental_dice_color or color == DieColor.OMNI:
                selected.append(sorted_colors[cid][1])
            if len(selected) == cost.elemental_dice_number:
                break
        else:
            raise ValueError("Not enough dice")
    # then select any
    if cost.any_dice_number > 0:
        for cid in range(len(sorted_colors) - 1, -1, -1):
            if sorted_colors[cid][1] not in selected:
                selected.append(sorted_colors[cid][1])
            if len(selected) == cost.any_dice_number + cost.elemental_dice_number:
                break
        else:
            raise ValueError("Not enough dice")
    return selected
