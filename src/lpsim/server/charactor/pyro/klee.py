from typing import Any, List, Literal

from ...action import Actions, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class JumpyDumpty(ElementalSkillBase):
    name: Literal['Jumpy Dumpty'] = 'Jumpy Dumpty'
    desc: str = '''Deals 3 Pyro DMG. This character gains Explosive Spark.'''
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        status_usage = 1
        if self.is_talent_equipped(match):
            status_usage = 2
        return super().get_actions(match) + [
            self.create_charactor_status('Explosive Spark', {
                'usage': status_usage,
                'max_usage': status_usage,
            })
        ]


class SparksNSplash(ElementalBurstBase):
    name: Literal["Sparks 'n' Splash"] = "Sparks 'n' Splash"
    desc: str = (
        "Deals 3 Pyro DMG, creates 1 Sparks 'n' Splash at the opponent's "
        "play area."
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Create teams status on opposite, so cannot call self.create_team_status
        """
        position = ObjectPosition(
            player_idx = 1 - self.position.player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1
        )
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name = self.name,
                object_position = position,
                object_arguments = {}
            )
        ]


# Talents


class PoundingSurprise(SkillTalent):
    name: Literal['Pounding Surprise']
    desc: str = (
        'Combat Action: When your active character is Klee, equip this card. '
        'After Klee equips this card, immediately use Jumpy Dumpty once. '
        'When your Klee, who has this card equipped, creates an Explosive '
        'Spark, its Usage(s) +1.'
    )
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Klee'] = 'Klee'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
    )
    skill: JumpyDumpty = JumpyDumpty()


# charactor base


class Klee(CharactorBase):
    name: Literal['Klee']
    version: Literal['3.4'] = '3.4'
    desc: str = '''"Fleeing Sunlight" Klee'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase | JumpyDumpty | SparksNSplash
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: PoundingSurprise | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Kaboom!',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            JumpyDumpty(),
            SparksNSplash(),
        ]
