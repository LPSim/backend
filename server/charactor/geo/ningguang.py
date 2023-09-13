from typing import Any, List, Literal

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class JadeScreen(ElementalSkillBase):
    name: Literal['Jade Screen'] = 'Jade Screen'
    desc: str = '''Deals 2 Geo DMG, creates 1 Jade Screen.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status(self.name),
        ]


class Starshatter(ElementalBurstBase):
    name: Literal['Starshatter'] = 'Starshatter'
    desc: str = (
        'Deals 6 Geo DMG. If Jade Screen is on the field, deals +2 DMG.'
    )
    damage: int = 6
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Check if Jade Screen exists. If so, change self.damage to 8.
        """
        status = match.player_tables[self.position.player_idx].team_status
        screen_exist: bool = False
        for s in status:
            if s.name == 'Jade Screen':
                screen_exist = True
                break
        if screen_exist:
            # temporary change damage to 8
            self.damage = 8
        ret = super().get_actions(match)
        self.damage = 6
        return ret


# Talents


class StrategicReserve(SkillTalent):
    name: Literal['Strategic Reserve']
    desc: str = (
        'Combat Action: When your active character is Ningguang, equip this '
        'card. After Ningguang equips this card, immediately use Jade Screen '
        'once. When your Ningguang, who has this card equipped, is on the '
        'field, Jade Screen will cause you to deal +1 Geo DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Ningguang'] = 'Ningguang'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 4,
    )
    skill: JadeScreen = JadeScreen()


# charactor base


class Ningguang(CharactorBase):
    name: Literal['Ningguang']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Eclipsing Star" Ningguang'''
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase | JadeScreen | Starshatter
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: StrategicReserve | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Sparkling Scatter',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            JadeScreen(),
            Starshatter(),
        ]
