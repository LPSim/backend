from typing import Any, List, Literal

from ...event import ChangeObjectUsageEventArguments, CreateObjectEventArguments

from ....utils.class_registry import register_class

from ...action import Actions, ChangeObjectUsageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
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


# Character status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear
# Skills


class SecretRiteChasmicSoulfarer(ElementalSkillBase):
    name: Literal["Secret Rite: Chasmic Soulfarer"] = "Secret Rite: Chasmic Soulfarer"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When talent equipped and level match, increase damage by 1
        """
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        talent = character.talent
        if talent is not None:
            status = (
                match.player_tables[self.position.player_idx]
                .characters[self.position.character_idx]
                .status
            )
            for s in status:
                if s.name == "Pactsworn Pathclearer":  # pragma: no branch
                    if s.usage in talent.active_levels:
                        self.damage = 4
                    break
            else:
                raise AssertionError("No Pactsworn Pathclearer status")
        ret = super().get_actions(match)
        self.damage = 3
        return ret


class SacredRiteWolfsSwiftness(ElementalBurstBase):
    name: Literal["Sacred Rite: Wolf's Swiftness"] = "Sacred Rite: Wolf's Swiftness"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=4, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        attack and increase usage
        """
        ret = super().get_actions(match)
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if s.name == "Pactsworn Pathclearer":  # pragma: no branch
                ret.append(
                    ChangeObjectUsageAction(object_position=s.position, change_usage=2)
                )
                return ret
        else:
            raise AssertionError("No Pactsworn Pathclearer status")


class LawfulEnforcer(CreateStatusPassiveSkill):
    name: Literal["Lawful Enforcer"] = "Lawful Enforcer"
    status_name: Literal["Pactsworn Pathclearer"] = "Pactsworn Pathclearer"


# Talents


class FeatherfallJudgment_3_3(SkillTalent):
    name: Literal["Featherfall Judgment"]
    version: Literal["3.3"] = "3.3"
    character_name: Literal["Cyno"] = "Cyno"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO,
        elemental_dice_number=3,
    )
    skill: Literal["Secret Rite: Chasmic Soulfarer"] = "Secret Rite: Chasmic Soulfarer"
    active_levels: List[int] = [3, 5]


class FeatherfallJudgment_4_2(SkillTalent):
    name: Literal["Featherfall Judgment"]
    version: Literal["4.2"] = "4.2"
    character_name: Literal["Cyno"] = "Cyno"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO,
        elemental_dice_number=3,
    )
    skill: Literal["Secret Rite: Chasmic Soulfarer"] = "Secret Rite: Chasmic Soulfarer"
    active_levels: List[int] = [0, 2, 4, 6]


# character base


class Cyno_3_3(CharacterBase):
    name: Literal["Cyno"]
    desc: Literal["", "transform"] = ""
    version: Literal["3.3"] = "3.3"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | SecretRiteChasmicSoulfarer
        | SacredRiteWolfsSwiftness
        | LawfulEnforcer
    ] = []
    faction: List[FactionType] = [FactionType.SUMERU]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Invoker's Spear",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SecretRiteChasmicSoulfarer(),
            SacredRiteWolfsSwiftness(),
            LawfulEnforcer(),
        ]

    def _update_desc(self, match: Any):
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if s.name == "Pactsworn Pathclearer":  # pragma: no branch
                if s.usage >= 4:
                    self.desc = "transform"
                else:
                    self.desc = ""
                return
        self.desc = ""

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Any
    ) -> List[Actions]:
        self._update_desc(match)
        return []

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[Actions]:
        self._update_desc(match)
        return []


register_class(Cyno_3_3 | FeatherfallJudgment_3_3 | FeatherfallJudgment_4_2)
