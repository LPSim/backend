from typing import Any, List, Literal

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
    desc: str = '''Deals 3 Cryo DMG, creates 1 Chonghua Frost Field.'''
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
        if self.is_talent_equipped(match):
            args = {
                'talent_activated': True,
                'usage': 3,
                'max_usage': 3
            }
        return super().get_actions(match) + [
            self.create_team_status("Chonghua's Frost Field", args),
        ]


# Talents


class SteadyBreathing(SkillTalent):
    name: Literal['Steady Breathing']
    desc: str = (
        'Combat Action: When your active character is Chongyun, equip this '
        "card. After Chongyun equips this card, immediately use Chonghua's "
        'Layered Frost once. When your Chongyun, who has this card equipped, '
        'creates a Chonghua Frost Field, it will have the following effects: '
        'Starting Duration (Rounds) +1, will cause your Sword, Claymore, and '
        "Polearm-wielding characters' Normal Attacks to deal +1 DMG."
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Chongyun'] = 'Chongyun'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4
    )
    skill: ChonghuasLayeredFrost = ChonghuasLayeredFrost()


# charactor base


class Chongyun(CharactorBase):
    name: Literal['Chongyun']  # Do not set default value for charactor name
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Frozen Ardor" Chongyun'''
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
    talent: SteadyBreathing | None = None

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
