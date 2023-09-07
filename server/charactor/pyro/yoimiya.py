from typing import Any, List, Literal

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
    desc: str = (
        'This character gains Niwabi Enshou. '
        '(This Skill does not grant Energy)'
    )
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
        return [self.create_charactor_status('Niwabi Enshou')]


class RyuukinSaxifrage(ElementalBurstBase):
    name: Literal['Ryuukin Saxifrage'] = 'Ryuukin Saxifrage'
    desc: str = '''Deals 3 Pyro DMG, creates 1 Aurous Blaze.'''
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


class NaganoharaMeteorSwarm(SkillTalent):
    name: Literal['Naganohara Meteor Swarm']
    desc: str = (
        'Combat Action: When your active character is Yoimiya, equip this '
        'card. After Yoimiya equips this card, immediately use Niwabi '
        'Fire-Dance once. After your Yoimiya, who has this card equipped, '
        'triggers Niwabi Enshou: Deal 1 additional Pyro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Yoimiya'] = 'Yoimiya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2,
    )
    skill: NiwabiFireDance = NiwabiFireDance()


# charactor base


class Yoimiya(CharactorBase):
    name: Literal['Yoimiya']  # Do not set default value for charactor name
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Frolicking Flames" Yoimiya'''
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
    talent: NaganoharaMeteorSwarm | None = None

    def _init_skills(self) -> None:
        self.skills = [
            FireworkFlareUp(),
            NiwabiFireDance(),
            RyuukinSaxifrage()
        ]
