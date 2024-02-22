from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import RoundPrepareEventArguments, SkillEndEventArguments

from ...action import Actions, ChargeAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Skills


class ClawAndThunder(ElementalSkillBase):
    name: Literal["Claw and Thunder"] = "Claw and Thunder"
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = ElementalSkillBase.get_cost(ElementType.ELECTRO)


class LightningFang(ElementalBurstBase):
    name: Literal["Lightning Fang"] = "Lightning Fang"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_character_status("The Wolf Within")
        ]


# Talents
class Awakening_4_2(SkillTalent):
    name: Literal["Awakening"]
    version: Literal["4.2"] = "4.2"
    character_name: Literal["Razor"] = "Razor"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO,
        elemental_dice_number=3,
    )
    skill: Literal["Claw and Thunder"] = "Claw and Thunder"
    usage: int = 1
    max_usage: int = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        reset usage
        """
        self.usage = self.max_usage
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        If equipped and use elemental skill, charge one of our electro
        character
        """
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
            source_area=ObjectPositionType.CHARACTER,
        ):
            # not equipped, or this character use skill
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        # find charge target
        table = match.player_tables[self.position.player_idx]
        characters = table.characters
        active = characters[table.active_character_idx]
        target_idx = -1
        if active.element == ElementType.ELECTRO and active.charge < active.max_charge:
            # active electro and not full charge
            target_idx = table.active_character_idx
        else:
            # check other characters
            for chraractor_idx, character in enumerate(characters):
                if (
                    character.element == ElementType.ELECTRO
                    and character.charge < character.max_charge
                    and character.is_alive
                ):
                    target_idx = chraractor_idx
                    break
        if target_idx == -1:
            # no target
            return []
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        # charge target
        return [
            ChargeAction(
                player_idx=self.position.player_idx, character_idx=target_idx, charge=1
            )
        ]


# character base


class Razor_3_8(CharacterBase):
    name: Literal["Razor"]
    version: Literal["3.8"] = "3.8"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | ClawAndThunder | LightningFang] = []
    faction: List[FactionType] = [FactionType.MONDSTADT]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Steel Fang",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ClawAndThunder(),
            LightningFang(),
        ]


register_class(Razor_3_8 | Awakening_4_2)
