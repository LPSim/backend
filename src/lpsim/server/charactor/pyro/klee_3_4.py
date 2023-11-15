from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class JumpyDumpty(ElementalSkillBase):
    name: Literal['Jumpy Dumpty'] = 'Jumpy Dumpty'
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


class PoundingSurprise_3_4(SkillTalent):
    name: Literal['Pounding Surprise']
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Klee'] = 'Klee'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Jumpy Dumpty'] = 'Jumpy Dumpty'


# charactor base


class Klee_3_4(CharactorBase):
    name: Literal['Klee']
    version: Literal['3.4'] = '3.4'
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

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Kaboom!',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            JumpyDumpty(),
            SparksNSplash(),
        ]


register_class(Klee_3_4 | PoundingSurprise_3_4)
