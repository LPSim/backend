from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import MakeDamageEventArguments, SkillEndEventArguments

from ...summon.base import SwirlChangeSummonBase

from ...action import Actions, CreateObjectAction, SwitchCharacterAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    ElementalReactionType,
    FactionType,
    ObjectPositionType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Summons


class AutumnWhirlwind_3_8(SwirlChangeSummonBase):
    name: Literal["Autumn Whirlwind"] = "Autumn Whirlwind"
    version: Literal["3.8"] = "3.8"
    usage: int = 3
    max_usage: int = 3
    damage: int = 1


# Skills


class Chihayaburu(ElementalSkillBase):
    name: Literal["Chihayaburu"] = "Chihayaburu"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        return [
            self.attack_opposite_active(
                match,
                self.damage,
                self.damage_type,
            ),
            self.create_character_status("Midare Ranzan: New"),
            self.charge_self(1),
        ]

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[SwitchCharacterAction]:
        if event.action.position.id != self.id:
            # not using this skill, do nothing
            return []
        # switch character
        next_character = match.player_tables[
            self.position.player_idx
        ].next_character_idx()
        if next_character is not None:
            return [
                SwitchCharacterAction(
                    player_idx=self.position.player_idx,
                    character_idx=next_character,
                )
            ]
        return []


class KazuhaSlash(ElementalBurstBase):
    name: Literal["Kazuha Slash"] = "Kazuha Slash"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon("Autumn Whirlwind"),
        ]


# Talents


class PoeticsOfFuubutsu_3_8(SkillTalent):
    name: Literal["Poetics of Fuubutsu"]
    version: Literal["3.8"] = "3.8"
    character_name: Literal["Kaedehara Kazuha"] = "Kaedehara Kazuha"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO,
        elemental_dice_number=3,
    )
    skill: Literal["Chihayaburu"] = "Chihayaburu"

    swirl_element = ElementType.NONE

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        when damage made, if it is from kazuha, and has swirl, record element.
        """
        for damage in event.damages:
            if not self.position.check_position_valid(
                damage.final_damage.position,
                match,
                player_idx_same=True,
                character_idx_same=True,
                target_area=ObjectPositionType.SKILL,
            ):
                # not self character use skill, do nothing
                continue
            if damage.final_damage.damage_from_element_reaction:
                # damage from elemental reaction, do nothing
                continue
            if damage.elemental_reaction != ElementalReactionType.SWIRL:
                # not swirl, do nothing
                continue
            assert (
                self.swirl_element == ElementType.NONE
            ), "element type already determined"
            # swirl, change element type
            elements = damage.reacted_elements
            assert elements[0] == ElementType.ANEMO, "First must be anemo"
            self.swirl_element = elements[1]
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If kazuha did skill and swirled, generate Poetics of Fuubutsu with
        corresponding element.
        """
        element = self.swirl_element
        # regardless of skill situation, reset swirl element
        self.swirl_element = ElementType.NONE
        if element == ElementType.NONE:
            # no swirl, do nothing
            return []
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
            source_area=ObjectPositionType.CHARACTER,
        ):  # pragma: no cover
            # not same player or character, or not skill, or not equipped
            return []
        # this character swirl, generate Poetics of Fuubutsu
        return [
            CreateObjectAction(
                object_name=f"{self.name}: {element.name.capitalize()}",
                object_position=ObjectPosition(
                    player_idx=self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        ]


# character base


class KaedeharaKazuha_3_8(CharacterBase):
    name: Literal["Kaedehara Kazuha"]
    version: Literal["3.8"] = "3.8"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | Chihayaburu | KazuhaSlash] = []
    faction: List[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Garyuu Bladework",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Chihayaburu(),
            KazuhaSlash(),
        ]


register_class(KaedeharaKazuha_3_8 | PoeticsOfFuubutsu_3_8 | AutumnWhirlwind_3_8)
