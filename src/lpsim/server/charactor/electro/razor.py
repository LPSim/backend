from typing import Any, List, Literal

from ..old_version.talent_cards_4_2 import Awakening_3_3

from ...event import RoundPrepareEventArguments, SkillEndEventArguments

from ...action import Actions, ChargeAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class ClawAndThunder(ElementalSkillBase):
    name: Literal['Claw and Thunder'] = 'Claw and Thunder'
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = ElementalSkillBase.get_cost(ElementType.ELECTRO)


class LightningFang(ElementalBurstBase):
    name: Literal['Lightning Fang'] = 'Lightning Fang'
    desc: str = (
        'Deals 3 Electro DMG. This character gains The Wolf Within.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_charactor_status('The Wolf Within')
        ]


# Talents


class Awakening(Awakening_3_3):
    version: Literal['4.2'] = '4.2'
    desc: str = (
        'Combat Action: When your active character is Razor, equip this card. '
        'After Razor equips this card, immediately use Claw and Thunder once. '
        'After your Razor, who has this card equipped, uses Claw and Thunder: '
        '1 of your Electro characters gains 1 Energy. '
        '(Active Character prioritized) (Once per round)'
    )
    usage: int = 1
    max_usage: int = 1
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )


# charactor base


class Razor(CharactorBase):
    name: Literal['Razor']
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Wolf Boy" Razor'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ClawAndThunder | LightningFang
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: Awakening | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Steel Fang',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ClawAndThunder(),
            LightningFang()
        ]
