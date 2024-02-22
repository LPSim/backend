from typing import Any, List, Literal

from ...event import CreateObjectEventArguments, RemoveObjectEventArguments

from ....utils.class_registry import register_class

from ...action import Actions

from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
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


class BaneOfAllEvil(ElementalBurstBase):
    name: Literal["Bane of All Evil"] = "Bane of All Evil"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If has talent, add skill cost decrease by 2
        """
        args = {}
        if self.is_talent_equipped(match):
            args["skill_cost_decrease_usage"] = 2
        return super().get_actions(match) + [
            self.create_character_status("Yaksha's Mask", args),
        ]


# Talents


class ConquerorOfEvilGuardianYaksha_3_7(SkillTalent):
    name: Literal["Conqueror of Evil: Guardian Yaksha"]
    version: Literal["3.7"] = "3.7"
    character_name: Literal["Xiao"] = "Xiao"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )
    skill: Literal["Bane of All Evil"] = "Bane of All Evil"


# character base


class Xiao_3_7(CharacterBase):
    name: Literal["Xiao"]
    desc: Literal["", "transform"] = ""
    version: Literal["3.7"] = "3.7"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | ElementalSkillBase | BaneOfAllEvil] = []
    faction: List[FactionType] = [FactionType.LIYUE]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Whirlwind Thrust",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name="Lemniscatic Wind Cycling",
                damage_type=DamageElementalType.ANEMO,
                cost=ElementalSkillBase.get_cost(self.element),
            ),
            BaneOfAllEvil(),
        ]

    def _update_desc(self, match):
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if s.name == "Yaksha's Mask":
                self.desc = "transform"
                return
        else:
            self.desc = ""

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        self._update_desc(match)
        return []

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[Actions]:
        self._update_desc(match)
        return []


register_class(Xiao_3_7 | ConquerorOfEvilGuardianYaksha_3_7)
