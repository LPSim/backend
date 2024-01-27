from typing import List, Tuple, Literal

from .character.character_base import CharacterBase
from .consts import (
    ElementType,
    ElementalReactionType,
    DamageElementalType,
    DamageType,
    ELEMENT_TO_DAMAGE_TYPE,
    ObjectPositionType,
)
from .modifiable_values import DamageElementEnhanceValue, DamageIncreaseValue
from .action import CreateObjectAction
from .struct import ObjectPosition


def check_elemental_reaction(
    source: ElementType, targets: List[ElementType]
) -> Tuple[ElementalReactionType, List[ElementType], List[ElementType]]:
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
    assert len(targets) <= 2, f"Two element application at most, got {targets}."
    if len(targets) == 2:
        assert targets == [ElementType.CRYO, ElementType.DENDRO], (
            "Two element application must be cryo and dendro." f"Got {targets}."
        )
    assert ElementType.GEO not in targets, "Geo cannot be applied to enemies."
    assert ElementType.ANEMO not in targets, "Anemo cannot be applied to enemies."
    if source == ElementType.NONE:
        return ElementalReactionType.NONE, [], targets
    elif source == ElementType.CRYO:
        if ElementType.PYRO in targets:
            return (
                ElementalReactionType.MELT,
                [ElementType.PYRO, ElementType.CRYO],
                [],
            )
        elif ElementType.HYDRO in targets:
            return (
                ElementalReactionType.FROZEN,
                [ElementType.HYDRO, ElementType.CRYO],
                [],
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.SUPERCONDUCT,
                [ElementType.ELECTRO, ElementType.CRYO],
                [],
            )
        else:
            new_targets = [ElementType.CRYO]
            if ElementType.DENDRO in targets:
                new_targets.append(ElementType.DENDRO)
            return (ElementalReactionType.NONE, [], new_targets)
    elif source == ElementType.HYDRO:
        if ElementType.PYRO in targets:
            return (
                ElementalReactionType.VAPORIZE,
                [ElementType.HYDRO, ElementType.PYRO],
                [],
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.FROZEN,
                [ElementType.HYDRO, ElementType.CRYO],
                targets[1:],  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.ELECTROCHARGED,
                [ElementType.ELECTRO, ElementType.HYDRO],
                [],
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.BLOOM,
                [ElementType.HYDRO, ElementType.DENDRO],
                [],
            )
        else:
            return (ElementalReactionType.NONE, [], [ElementType.HYDRO])
    elif source == ElementType.PYRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.VAPORIZE,
                [ElementType.HYDRO, ElementType.PYRO],
                [],
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.MELT,
                [ElementType.PYRO, ElementType.CRYO],
                targets[1:],  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.OVERLOADED,
                [ElementType.PYRO, ElementType.ELECTRO],
                [],
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.BURNING,
                [ElementType.PYRO, ElementType.DENDRO],
                [],
            )
        else:
            return (ElementalReactionType.NONE, [], [ElementType.PYRO])
    elif source == ElementType.ELECTRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.ELECTROCHARGED,
                [ElementType.ELECTRO, ElementType.HYDRO],
                [],
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.SUPERCONDUCT,
                [ElementType.ELECTRO, ElementType.CRYO],
                targets[1:],  # cryo must be first
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.OVERLOADED,
                [ElementType.PYRO, ElementType.ELECTRO],
                [],
            )
        elif ElementType.DENDRO in targets:
            return (
                ElementalReactionType.QUICKEN,
                [ElementType.ELECTRO, ElementType.DENDRO],
                [],
            )
        else:
            return (ElementalReactionType.NONE, [], [ElementType.ELECTRO])
    elif source == ElementType.GEO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE,
                [ElementType.GEO, ElementType.HYDRO],
                [],
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE,
                [ElementType.GEO, ElementType.PYRO],
                [],
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE,
                [ElementType.GEO, ElementType.CRYO],
                targets[1:],  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.CRYSTALLIZE,
                [ElementType.GEO, ElementType.ELECTRO],
                [],
            )
        else:
            return (ElementalReactionType.NONE, [], targets)
    elif source == ElementType.DENDRO:
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.BLOOM,
                [ElementType.HYDRO, ElementType.DENDRO],
                [],
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.BURNING,
                [ElementType.PYRO, ElementType.DENDRO],
                [],
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.QUICKEN,
                [ElementType.ELECTRO, ElementType.DENDRO],
                [],
            )
        else:
            new_targets = [ElementType.DENDRO]
            if ElementType.CRYO in targets:
                new_targets = [ElementType.CRYO, ElementType.DENDRO]
            return (ElementalReactionType.NONE, [], new_targets)
    else:
        assert source == ElementType.ANEMO
        if ElementType.HYDRO in targets:
            return (
                ElementalReactionType.SWIRL,
                [ElementType.ANEMO, ElementType.HYDRO],
                [],
            )
        elif ElementType.PYRO in targets:
            return (
                ElementalReactionType.SWIRL,
                [ElementType.ANEMO, ElementType.PYRO],
                [],
            )
        elif ElementType.CRYO in targets:
            return (
                ElementalReactionType.SWIRL,
                [ElementType.ANEMO, ElementType.CRYO],
                targets[1:],  # cryo must be first
            )
        elif ElementType.ELECTRO in targets:
            return (
                ElementalReactionType.SWIRL,
                [ElementType.ANEMO, ElementType.ELECTRO],
                [],
            )
        else:
            return (ElementalReactionType.NONE, [], targets)


def apply_elemental_reaction(
    target_characters: List[CharacterBase],
    active_character_idx: int,
    damage: DamageElementEnhanceValue,
    reaction: ElementalReactionType,
    reacted_elements: List[ElementType],
    version: Literal["3.3", "3.4"],
) -> Tuple[
    DamageIncreaseValue, List[DamageElementEnhanceValue], CreateObjectAction | None
]:
    """
    Apply elemental reaction to DamageElementEnhanceValue, and
    generate DamageIncreaseValue.
    It returns a DamageIncreaseValue related to input damage, and a list of
    DamageElementEnhanceValue that generated by elemental reaction. If new
    objects are generated with this elemental reaction, it will also return
    the CreateObjectAction.
    """
    res: List[DamageElementEnhanceValue] = []
    damage = DamageIncreaseValue.from_element_enhance_value(
        damage, reaction, reacted_elements
    )
    target_position = damage.target_position
    create_object = elemental_reaction_side_effect(
        reaction,
        target_position.player_idx,
        target_position.character_idx,
        version=version,
    )
    if reaction == ElementalReactionType.NONE:
        return damage, res, create_object
    if damage.damage_type != DamageType.DAMAGE:
        return damage, res, create_object
    if reaction in [
        ElementalReactionType.MELT,
        ElementalReactionType.VAPORIZE,
        ElementalReactionType.OVERLOADED,
    ]:
        # +2 damage types
        damage.damage += 2
    elif reaction == ElementalReactionType.SWIRL:
        # special swirl, 1 elemental damage for other characters
        element_type = reacted_elements[1]
        assert element_type != ElementType.ANEMO, "Anemo should always be first"
        attack_target = damage.target_position.character_idx
        for cnum in range(0, len(target_characters)):
            cnum = (cnum + active_character_idx) % len(target_characters)
            if cnum == attack_target:
                continue
            c = target_characters[cnum]
            if c.is_alive:
                res.append(
                    DamageElementEnhanceValue(
                        position=damage.position,
                        target_position=ObjectPosition(
                            player_idx=damage.target_position.player_idx,
                            character_idx=cnum,
                            area=damage.target_position.area,
                            id=c.id,
                        ),
                        damage=1,
                        damage_type=DamageType.DAMAGE,
                        damage_elemental_type=ELEMENT_TO_DAMAGE_TYPE[element_type],
                        cost=damage.cost.copy(),
                        damage_from_element_reaction=True,
                    )
                )
    else:
        # all others are +1 damage types
        damage.damage += 1
        if reaction in [
            ElementalReactionType.ELECTROCHARGED,
            ElementalReactionType.SUPERCONDUCT,
        ]:
            # 1 piercing dmg for other characters
            damage_type = DamageElementalType.PIERCING
            attack_target = damage.target_position.character_idx
            for cnum in range(0, len(target_characters)):
                cnum = (cnum + active_character_idx) % len(target_characters)
                if cnum == attack_target:
                    continue
                c = target_characters[cnum]
                if c.is_alive:
                    res.append(
                        DamageElementEnhanceValue(
                            position=damage.position,
                            target_position=ObjectPosition(
                                player_idx=damage.target_position.player_idx,
                                character_idx=cnum,
                                area=damage.target_position.area,
                                id=c.id,
                            ),
                            damage=1,
                            damage_type=DamageType.DAMAGE,
                            damage_elemental_type=damage_type,
                            cost=damage.cost.copy(),
                            damage_from_element_reaction=True,
                        )
                    )
    return damage, res, create_object


def elemental_reaction_side_effect_ver_3_4(
    reaction: ElementalReactionType, player_idx: int, character_idx: int
) -> CreateObjectAction | None:
    """
    Apply side effect of elemental reaction.
    """
    if reaction == ElementalReactionType.FROZEN:
        position = ObjectPosition(
            player_idx=player_idx,
            character_idx=character_idx,
            area=ObjectPositionType.CHARACTER_STATUS,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position, object_name="Frozen", object_arguments={}
        )
    elif reaction == ElementalReactionType.CRYSTALLIZE:
        position = ObjectPosition(
            player_idx=1 - player_idx,
            area=ObjectPositionType.TEAM_STATUS,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position, object_name="Crystallize", object_arguments={}
        )
    elif reaction == ElementalReactionType.BURNING:
        position = ObjectPosition(
            player_idx=1 - player_idx,
            area=ObjectPositionType.SUMMON,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position, object_name="Burning Flame", object_arguments={}
        )
    elif reaction == ElementalReactionType.BLOOM:
        position = ObjectPosition(
            player_idx=1 - player_idx,
            area=ObjectPositionType.TEAM_STATUS,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position, object_name="Dendro Core", object_arguments={}
        )
    elif reaction == ElementalReactionType.QUICKEN:
        position = ObjectPosition(
            player_idx=1 - player_idx,
            area=ObjectPositionType.TEAM_STATUS,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position,
            object_name="Catalyzing Field",
            object_arguments={},
        )
    return None


def elemental_reaction_side_effect_ver_3_3(
    reaction: ElementalReactionType, player_idx: int, character_idx: int
) -> CreateObjectAction | None:
    """
    Apply side effect of elemental reaction. In 3.3, only quicken is different.
    """
    if reaction == ElementalReactionType.QUICKEN:
        position = ObjectPosition(
            player_idx=1 - player_idx,
            area=ObjectPositionType.TEAM_STATUS,
            id=-1,
        )
        return CreateObjectAction(
            object_position=position,
            object_name="Catalyzing Field",
            object_arguments={"version": "3.3"},
        )
    return elemental_reaction_side_effect_ver_3_4(reaction, player_idx, character_idx)


def elemental_reaction_side_effect(
    reaction: ElementalReactionType,
    player_idx: int,
    character_idx: int,
    version: Literal["3.3", "3.4"] = "3.4",
) -> CreateObjectAction | None:
    if version == "3.3":
        return elemental_reaction_side_effect_ver_3_3(
            reaction, player_idx, character_idx
        )
    return elemental_reaction_side_effect_ver_3_4(reaction, player_idx, character_idx)
