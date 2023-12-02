from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions, ChangeObjectUsageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    CreateStatusPassiveSkill, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear
# Skills


class SecretRiteChasmicSoulfarer(ElementalSkillBase):
    name: Literal[
        'Secret Rite: Chasmic Soulfarer'] = 'Secret Rite: Chasmic Soulfarer'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When talent equipped and level match, increase damage by 1
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent = charactor.talent
        if talent is not None:
            status = match.player_tables[self.position.player_idx].charactors[
                self.position.charactor_idx].status
            for s in status:
                if s.name == 'Pactsworn Pathclearer':  # pragma: no branch
                    if s.usage in talent.active_levels:
                        self.damage = 4
                    break
            else:
                raise AssertionError('No Pactsworn Pathclearer status')
        ret = super().get_actions(match)
        self.damage = 3
        return ret


class SacredRiteWolfsSwiftness(ElementalBurstBase):
    name: Literal[
        "Sacred Rite: Wolf's Swiftness"] = "Sacred Rite: Wolf's Swiftness"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        attack and increase usage
        """
        ret = super().get_actions(match)
        status = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx].status
        for s in status:
            if s.name == 'Pactsworn Pathclearer':  # pragma: no branch
                ret.append(ChangeObjectUsageAction(
                    object_position = s.position,
                    change_usage = 2
                ))
                return ret
        else:
            raise AssertionError('No Pactsworn Pathclearer status')


class LawfulEnforcer(CreateStatusPassiveSkill):
    name: Literal['Lawful Enforcer'] = 'Lawful Enforcer'
    status_name: Literal['Pactsworn Pathclearer'] = 'Pactsworn Pathclearer'


# Talents


class FeatherfallJudgment_3_3(SkillTalent):
    name: Literal['Featherfall Judgment']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Cyno'] = 'Cyno'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal[
        'Secret Rite: Chasmic Soulfarer'
    ] = 'Secret Rite: Chasmic Soulfarer'
    active_levels: List[int] = [3, 5]


class FeatherfallJudgment_4_2(SkillTalent):
    name: Literal['Featherfall Judgment']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Cyno'] = 'Cyno'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal[
        'Secret Rite: Chasmic Soulfarer'
    ] = 'Secret Rite: Chasmic Soulfarer'
    active_levels: List[int] = [0, 2, 4, 6]


# charactor base


class Cyno_3_3(CharactorBase):
    name: Literal['Cyno']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SecretRiteChasmicSoulfarer
        | SacredRiteWolfsSwiftness | LawfulEnforcer
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = "Invoker's Spear",
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SecretRiteChasmicSoulfarer(),
            SacredRiteWolfsSwiftness(),
            LawfulEnforcer()
        ]


register_class(Cyno_3_3 | FeatherfallJudgment_3_3 | FeatherfallJudgment_4_2)
