from typing import List, Tuple, Literal
from . import Charactors
from .consts import (
    ElementType, ElementalReactionType, DamageElementalType,
    DamageType, ELEMENT_TO_DAMAGE_TYPE, ObjectPositionType,
)
from .modifiable_values import DamageElementEnhanceValue, DamageIncreaseValue
from .action import Actions, CreateObjectAction
from .struct import ObjectPosition


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
    elif source == ElementType.CRYO:
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
    elif source == ElementType.HYDRO:
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
    elif source == ElementType.PYRO:
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
    elif source == ElementType.ELECTRO:
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
    elif source == ElementType.GEO:
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
                targets[1:]  # cryo must be first
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
    elif source == ElementType.DENDRO:
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
    else:
        assert source == ElementType.ANEMO
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
                targets[1:]  # cryo must be first
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
        damage: DamageElementEnhanceValue,
        reaction: ElementalReactionType,
        reacted_elements: List[ElementType]
) -> Tuple[DamageIncreaseValue, List[DamageElementEnhanceValue]]:
    """
    Apply elemental reaction to DamageElementEnhanceValue, and
    generate DamageIncreaseValue.
    It returns a DamageIncreaseValue related to input damage, and a list of
    DamageElementEnhanceValue that generated by elemental reaction.

    NOTE: Only direct damage will count, summons and status will not 
    considered to generate here.
    """
    res: List[DamageElementEnhanceValue] = []
    damage = DamageIncreaseValue.from_element_enhance_value(
        damage, reaction, reacted_elements
    )
    if reaction == ElementalReactionType.NONE:
        return damage, res
    if damage.damage_type != DamageType.DAMAGE:
        return damage, res
    if reaction in [ElementalReactionType.MELT,
                    ElementalReactionType.VAPORIZE,
                    ElementalReactionType.OVERLOADED]:
        # +2 damage types
        damage.damage += 2
    elif reaction == ElementalReactionType.SWIRL:
        # special swirl, 1 elemental damage for other charactors
        element_type = reacted_elements[1]
        assert element_type != ElementType.ANEMO, \
            'Anemo should always be first'
        attack_target = damage.target_position.charactor_idx
        for cnum in range(1, len(target_charactors)):
            cnum = (cnum + attack_target) % len(target_charactors)
            c = target_charactors[cnum]
            if c.is_alive:
                res.append(DamageElementEnhanceValue(
                    position = damage.position,
                    target_position = ObjectPosition(
                        player_idx = damage.target_position.player_idx,
                        charactor_idx = cnum,
                        area = damage.target_position.area,
                        id = c.id,
                    ),
                    damage = 1,
                    damage_type = DamageType.DAMAGE,
                    damage_elemental_type = ELEMENT_TO_DAMAGE_TYPE[
                        element_type],
                    cost = damage.cost.copy(),
                    damage_from_element_reaction = True
                ))
    else:
        # all others are +1 damage types
        damage.damage += 1
        if reaction in [ElementalReactionType.ELECTROCHARGED,
                        ElementalReactionType.SUPERCONDUCT]:
            # 1 piercing dmg for other charactors
            damage_type = DamageElementalType.PIERCING
            attack_target = damage.target_position.charactor_idx
            for cnum, c in enumerate(target_charactors):
                if cnum == attack_target:
                    continue
                if c.is_alive:
                    res.append(DamageElementEnhanceValue(
                        position = damage.position,
                        target_position = ObjectPosition(
                            player_idx = damage.target_position.player_idx,
                            charactor_idx = cnum,
                            area = damage.target_position.area,
                            id = c.id,
                        ),
                        damage = 1,
                        damage_type = DamageType.DAMAGE,
                        damage_elemental_type = damage_type,
                        cost = damage.cost.copy(),
                        damage_from_element_reaction = True
                    ))
    return damage, res


def elemental_reaction_side_effect_ver_3_4(
        reaction: ElementalReactionType, player_idx: int,
        charator_idx: int) -> Actions | None:
    """
    Apply side effect of elemental reaction. 
    """
    if reaction == ElementalReactionType.FROZEN:
        position = ObjectPosition(
            player_idx = player_idx,
            charactor_idx = charator_idx,
            area = ObjectPositionType.CHARACTOR_STATUS,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Frozen',
            object_arguments = {}
        )
    elif reaction == ElementalReactionType.CRYSTALLIZE:
        position = ObjectPosition(
            player_idx = 1 - player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Crystallize',
            object_arguments = {}
        )
    elif reaction == ElementalReactionType.BURNING:
        position = ObjectPosition(
            player_idx = 1 - player_idx,
            area = ObjectPositionType.SUMMON,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Burning Flame',
            object_arguments = {}
        )
    elif reaction == ElementalReactionType.BLOOM:
        position = ObjectPosition(
            player_idx = 1 - player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Dendro Core',
            object_arguments = {}
        )
    elif reaction == ElementalReactionType.QUICKEN:
        position = ObjectPosition(
            player_idx = 1 - player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Catalyzing Field',
            object_arguments = {}
        )
    return None


def elemental_reaction_side_effect_ver_3_3(
        reaction: ElementalReactionType, player_idx: int,
        charator_idx: int) -> Actions | None:
    """
    Apply side effect of elemental reaction. In 3.3, only quicken is different.
    """
    if reaction == ElementalReactionType.QUICKEN:
        position = ObjectPosition(
            player_idx = 1 - player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1,
        )
        return CreateObjectAction(
            object_position = position,
            object_name = 'Catalyzing Field',
            object_arguments = { 'version': '3.3' }
        )
    return elemental_reaction_side_effect_ver_3_4(
        reaction, player_idx, charator_idx
    )


def elemental_reaction_side_effect(
        reaction: ElementalReactionType, player_idx: int,
        charator_idx: int, version: Literal['3.3', '3.4'] = '3.4'
) -> Actions | None:
    if version == '3.3':
        return elemental_reaction_side_effect_ver_3_3(
            reaction, player_idx, charator_idx
        )
    return elemental_reaction_side_effect_ver_3_4(
        reaction, player_idx, charator_idx
    )
