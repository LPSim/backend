from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Skills


class FireworkFlareUp(PhysicalNormalAttackBase):
    name: Literal['Firework Flare-Up'] = 'Firework Flare-Up'
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.PYRO)


class NiwabiFireDance(ElementalSkillBase):
    name: Literal['Niwabi Fire-Dance'] = 'Niwabi Fire-Dance'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 1
    )

    def get_actions(self, match: Any) -> List[CreateObjectAction]:
        """
        only create object
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent = charactor.talent
        max_usage = 2
        if talent is not None:
            max_usage = talent.status_max_usage
        return [self.create_charactor_status('Niwabi Enshou', {
            'usage': max_usage,
            'max_usage': max_usage
        })]


class RyuukinSaxifrage(ElementalBurstBase):
    name: Literal['Ryuukin Saxifrage'] = 'Ryuukin Saxifrage'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status('Aurous Blaze')
        ]


# Talents


class NaganoharaMeteorSwarm_4_2(SkillTalent):
    name: Literal['Naganohara Meteor Swarm']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Yoimiya'] = 'Yoimiya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2,
    )
    skill: Literal['Niwabi Fire-Dance'] = 'Niwabi Fire-Dance'
    status_max_usage: int = 3


# charactor base


class Yoimiya_3_8(CharactorBase):
    name: Literal['Yoimiya']  # Do not set default value for charactor name
    version: Literal['3.8'] = '3.8'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        FireworkFlareUp | NiwabiFireDance | RyuukinSaxifrage
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            FireworkFlareUp(),
            NiwabiFireDance(),
            RyuukinSaxifrage()
        ]


register_class(Yoimiya_3_8 | NaganoharaMeteorSwarm_4_2)
