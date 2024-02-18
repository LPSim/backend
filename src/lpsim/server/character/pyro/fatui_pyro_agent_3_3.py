from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import CreateObjectEventArguments
from ...action import Actions, ChangeObjectUsageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    WeaponType,
)
from ..character_base import (
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Skills


class Prowl(ElementalSkillBase):
    name: Literal["Prowl"] = "Prowl"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [self.create_character_status("Stealth")]


class StealthMaster(CreateStatusPassiveSkill):
    name: Literal["Stealth Master"] = "Stealth Master"
    status_name: Literal["Stealth"] = "Stealth"
    regenerate_when_revive: bool = False


# Talents


class PaidinFull_3_3(SkillTalent):
    name: Literal["Paid in Full"]
    version: Literal["3.3"] = "3.3"
    character_name: Literal["Fatui Pyro Agent"] = "Fatui Pyro Agent"
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)
    skill: Literal["Prowl"] = "Prowl"

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        When create object, check if it is stealth
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped, do nothing
            return []
        if not self.position.check_position_valid(
            event.action.object_position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.CHARACTER_STATUS,
        ):
            # not self create character status, do nothing
            return []
        if event.action.object_name != "Stealth":
            # not stealth, do nothing
            return []
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        status = None
        for s in character.status:
            if s.name == "Stealth":
                status = s
                break
        else:
            raise AssertionError("Stealth not found")
        # add 1 usage
        return [
            ChangeObjectUsageAction(object_position=status.position, change_usage=1)
        ]


# character base


class FatuiPyroAgent_3_3(CharacterBase):
    name: Literal["Fatui Pyro Agent"]
    version: Literal["3.3"] = "3.3"
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Prowl | ElementalBurstBase | StealthMaster
    ] = []
    faction: List[FactionType] = [FactionType.FATUI]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Thrust",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Prowl(),
            ElementalBurstBase(
                name="Blade Ablaze",
                damage=5,
                damage_type=DamageElementalType.PYRO,
                cost=ElementalBurstBase.get_cost(self.element, 3, 2),
            ),
            StealthMaster(),
        ]


register_class(FatuiPyroAgent_3_3 | PaidinFull_3_3)
