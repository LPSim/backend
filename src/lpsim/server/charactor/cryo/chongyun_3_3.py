from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear
# Skills


class ChonghuasLayeredFrost(ElementalSkillBase):
    name: Literal["Chonghua's Layered Frost"] = "Chonghua's Layered Frost"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        args = {}
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent = charactor.talent
        if talent is not None:
            args = {
                'talent_activated': True,
                'usage': talent.status_max_usage,
                'max_usage': talent.status_max_usage
            }
        return super().get_actions(match) + [
            self.create_team_status("Chonghua's Frost Field", args),
        ]


# Talents


class SteadyBreathing_3_3(SkillTalent):
    name: Literal['Steady Breathing']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Chongyun'] = 'Chongyun'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4
    )
    skill: Literal["Chonghua's Layered Frost"] = "Chonghua's Layered Frost"
    status_max_usage: int = 3


class SteadyBreathing_4_2(SkillTalent):
    name: Literal['Steady Breathing']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Chongyun'] = 'Chongyun'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    skill: Literal["Chonghua's Layered Frost"] = "Chonghua's Layered Frost"
    status_max_usage: int = 2


# charactor base


class Chongyun_3_3(CharactorBase):
    name: Literal['Chongyun']  # Do not set default value for charactor name
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase
        | ChonghuasLayeredFrost | ElementalBurstBase
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Demonbane',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ChonghuasLayeredFrost(),
            ElementalBurstBase(
                name = 'Cloud-Parting Star',
                damage = 7,
                damage_type = DamageElementalType.CRYO,
                cost = ElementalBurstBase.get_cost(self.element, 3, 3)
            )
        ]


register_class(Chongyun_3_3 | SteadyBreathing_3_3 | SteadyBreathing_4_2)
