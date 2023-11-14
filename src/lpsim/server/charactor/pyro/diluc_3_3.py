from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import CostValue
from ...event import RoundPrepareEventArguments

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)
# Skills


class SearingOnslaught(ElementalSkillBase):
    name: Literal['Searing Onslaught'] = 'Searing Onslaught'
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    counter: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, reset counter
        """
        self.counter = 0
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        If self equipped talent, reduce the second use cost by 1
        """
        if self.counter != 1:
            # not second use
            return value
        if not self.is_talent_equipped(match):
            # no talent
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, area_same = True, id_same = True
        ):
            # not this skill
            return value
        # decrease cost
        value.cost.decrease_cost(DieColor.PYRO)
        return value

    def get_actions(self, match: Any) -> List[Actions]:
        """
        if it is the third time to use, increase damage by 2
        """
        self.counter += 1
        if self.counter == 3:
            self.damage = 5
        ret = super().get_actions(match)
        self.damage = 3
        return ret


class Dawn(ElementalBurstBase):
    name: Literal['Dawn'] = 'Dawn'
    damage: int = 8
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_charactor_status(
                'Pyro Elemental Infusion',
                { 'mark': 'Diluc' }
            )
        ]


# Talents


class FlowingFlame_3_3(SkillTalent):
    name: Literal['Flowing Flame']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Diluc'] = 'Diluc'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Searing Onslaught'] = 'Searing Onslaught'


# charactor base


class Diluc_3_3(CharactorBase):
    name: Literal['Diluc']  # Do not set default value for charactor name
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | SearingOnslaught | Dawn
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Tempered Sword',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SearingOnslaught(),
            Dawn()
        ]


register_class(Diluc_3_3 | FlowingFlame_3_3)
