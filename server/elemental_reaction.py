from typing import List, Tuple
from .charactor import Charactors
from .consts import (
    ElementType, ElementalReactionType, DamageType,
    ELEMENT_TO_DAMAGE_TYPE
)
from .modifiable_values import DamageValue


def check_elemental_reaction(
    source: ElementType, targets: List[ElementType]
) -> Tuple[ElementalReactionType, List[ElementType], 
           List[ElementType]]:
    """
    Check the elemental reaction based on source and targets.

    Args:
        source (ElementType): The element type of attack source.
        targets (List[ElementType]): The element application of attack targets.

    Returns:
        Tuple[ElementalReactionType, List[ElementType], List[ElementType]]:
            The elemental reaction type, the element types that are consumed,
            and the element applications updated.
    """
    assert len(targets) <= 2, \
        f'Two element application at most, got {targets}.'
    if len(targets) == 2:
        assert targets == [ElementType.CRYO, ElementType.DENDRO], \
            'Two element application must be cryo and dendro.' \
            f'Got {targets}.'
    assert ElementType.GEO not in targets, \
        'Geo cannot be applied to enemies.'
    assert ElementType.ANEMO not in targets, \
        'Anemo cannot be applied to enemies.'
    if source == ElementType.NONE:
        return ElementalReactionType.NONE, [], targets
    if source == ElementType.CRYO:
        if ElementType.PYRO in targets:
            return (
                ElementalReactionType.MELT, 
                [ElementType.PYRO, ElementType.CRYO], 
                []
            )
        elif ElementType.HYDRO in targets:
            return (
                ElementalReactionType.FROZEN, 
                [ElementType.HYDRO, ElementType.CRYO], 
                []
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.SUPERCONDUCT, 
                [ElementType.ELECTRO, ElementType.CRYO], 
                []
            )
        else:
            new_targets = [ElementType.CRYO]
            if ElementType.DENDRO in targets:
                new_targets.append(ElementType.DENDRO)
            return (
                ElementalReactionType.NONE, 
                [], 
                new_targets
            )
    if source == ElementType.HYDRO:
        if ElementType.PYRO in targets:
            return (
                ElementalReactionType.VAPORIZE, 
                [ElementType.HYDRO, ElementType.PYRO], 
                []
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.FROZEN, 
                [ElementType.HYDRO, ElementType.CRYO], 
                targets[1:]  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.ELECTROCHARGED, 
                [ElementType.ELECTRO, ElementType.HYDRO], 
                []
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.BLOOM, 
                [ElementType.HYDRO, ElementType.DENDRO], 
                []
            )
        else:
            return (
                ElementalReactionType.NONE, 
                [], 
                [ElementType.HYDRO]
            )
    if source == ElementType.PYRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.VAPORIZE, 
                [ElementType.HYDRO, ElementType.PYRO], 
                []
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.MELT, 
                [ElementType.PYRO, ElementType.CRYO], 
                targets[1:]  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.OVERLOADED, 
                [ElementType.PYRO, ElementType.ELECTRO], 
                []
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.BURNING, 
                [ElementType.PYRO, ElementType.DENDRO], 
                []
            )
        else:
            return (
                ElementalReactionType.NONE, 
                [], 
                [ElementType.PYRO]
            )
    if source == ElementType.ELECTRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.ELECTROCHARGED, 
                [ElementType.ELECTRO, ElementType.HYDRO], 
                []
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.SUPERCONDUCT, 
                [ElementType.ELECTRO, ElementType.CRYO], 
                targets[1:]  # cryo must be first
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.OVERLOADED, 
                [ElementType.PYRO, ElementType.ELECTRO], 
                []
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.QUICKEN, 
                [ElementType.ELECTRO, ElementType.DENDRO], 
                []
            )
        else:
            return (
                ElementalReactionType.NONE, 
                [], 
                [ElementType.ELECTRO]
            )
    if source == ElementType.GEO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE, 
                [ElementType.GEO, ElementType.HYDRO], 
                []
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE, 
                [ElementType.GEO, ElementType.PYRO], 
                []
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE, 
                [ElementType.GEO, ElementType.CRYO], 
                targets[:1]  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE, 
                [ElementType.GEO, ElementType.ELECTRO], 
                []
            )
        else:
            return (
                ElementalReactionType.NONE, 
                [], 
                targets
            )
    if source == ElementType.DENDRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.BLOOM, 
                [ElementType.HYDRO, ElementType.DENDRO], 
                []
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.BURNING, 
                [ElementType.PYRO, ElementType.DENDRO], 
                []
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.QUICKEN, 
                [ElementType.ELECTRO, ElementType.DENDRO], 
                []
            )
        else:
            new_targets = [ElementType.DENDRO]
            if ElementType.CRYO in targets:
                new_targets = [ElementType.CRYO, ElementType.DENDRO]
            return (
                ElementalReactionType.NONE, 
                [], 
                new_targets
            )
    if source == ElementType.ANEMO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.SWIRL, 
                [ElementType.ANEMO, ElementType.HYDRO], 
                []
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.SWIRL, 
                [ElementType.ANEMO, ElementType.PYRO], 
                []
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.SWIRL, 
                [ElementType.ANEMO, ElementType.CRYO], 
                targets[:1]  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.SWIRL, 
                [ElementType.ANEMO, ElementType.ELECTRO], 
                []
            )
        else:
            return (
                ElementalReactionType.NONE, 
                [], 
                targets
            )


def apply_elemental_reaction(
        target_charactors: List[Charactors],
        damage: DamageValue,
        reaction: ElementalReactionType,
        reacted_elements: List[ElementType]) -> List[DamageValue]:
    """
    Apply elemental reaction to damage. Damage will be modified in-place.
    The modified damage will be
    the first element of the returned list. If the reaction generates
    more damages (e.g. superconduct), they will be the following elements.
    NOTE: Only direct damage will count, summons and status will not 
    considered to generate here.
    """
    res: List[DamageValue] = [damage]
    if reaction == ElementalReactionType.NONE:
        return res
    if damage.damage <= 0:
        # heal or no-damage element application, no need to change damage
        return res
    if reaction in [ElementalReactionType.MELT,
                    ElementalReactionType.VAPORIZE,
                    ElementalReactionType.OVERLOADED]:
        # +2 damage types
        damage.damage += 2
    elif reaction == ElementalReactionType.SWIRL:
        # special swirl, 1 elemental damage for other charactors
        element_type = reacted_elements[0]
        if element_type == ElementType.ANEMO:
            element_type = reacted_elements[1]
        attack_target = damage.target_charactor_id
        for cnum, c in enumerate(target_charactors):
            if cnum == attack_target:
                continue
            if c.is_alive:
                res.append(DamageValue(
                    target_player_id = damage.target_player_id,
                    target_charactor_id = cnum,
                    damage = 1,
                    damage_type = ELEMENT_TO_DAMAGE_TYPE[element_type],
                    charge_cost = 0,
                    damage_source_type = damage.damage_source_type
                ))
    else:
        # all others are +1 damage types
        damage.damage += 1
        if reaction in [ElementalReactionType.ELECTROCHARGED,
                        ElementalReactionType.SUPERCONDUCT]:
            # 1 piercing dmg for other charactors
            damage_type = DamageType.PIERCING
            attack_target = damage.target_charactor_id
            for cnum, c in enumerate(target_charactors):
                if cnum == attack_target:
                    continue
                if c.is_alive:
                    res.append(DamageValue(
                        target_player_id = damage.target_player_id,
                        target_charactor_id = cnum,
                        damage = 1,
                        damage_type = damage_type,
                        charge_cost = 0,
                        damage_source_type = damage.damage_source_type
                    ))
    return res
