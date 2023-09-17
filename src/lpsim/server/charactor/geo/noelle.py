from typing import Any, List, Literal

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    CharactorBase, PhysicalNormalAttackBase, SkillTalent
)


class Breastplate(ElementalSkillBase):
    name: Literal['Breastplate'] = 'Breastplate'
    desc: str = '''Deals 1 Geo DMG, creates 1 Full Plate.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.GEO
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_team_status('Full Plate'))
        return ret


class SweepingTime(ElementalBurstBase):
    name: Literal['Sweeping Time'] = 'Sweeping Time'
    desc: str = '''Deals 4 Geo DMG. This character gains Sweeping Time.'''
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_number = 4,
        elemental_dice_color = DieColor.GEO,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_charactor_status('Sweeping Time'))
        return ret


class IGotYourBack(SkillTalent):
    name: Literal['I Got Your Back']
    desc: str = (
        'Combat Action: When your active character is Noelle, equip this '
        'card. After Noelle equips this card, immediately use Breastplate '
        'once. When your Noelle, who has this card equipped, creates a Full '
        'Plate, it will heal all your characters for 1 HP after Noelle uses '
        'a Normal Attack. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Noelle'] = 'Noelle'
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.GEO
    )
    skill: Breastplate = Breastplate()


class Noelle(CharactorBase):
    name: Literal['Noelle']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Chivalric Blossom" Noelle'''
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Breastplate | SweepingTime
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: IGotYourBack | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework - Maid',
                cost = PhysicalNormalAttackBase.get_cost(
                    ElementType.GEO,
                )
            ),
            Breastplate(),
            SweepingTime()
        ]
