from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import DamageIncreaseValue
from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class GuideToAfterlife(ElementalSkillBase):
    name: Literal['Guide to Afterlife'] = 'Guide to Afterlife'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        gain charge and create status
        """
        return [
            self.charge_self(1),
            self.create_charactor_status('Paramita Papilio'),
        ]


class SpiritSoother(ElementalBurstBase):
    name: Literal['Spirit Soother'] = 'Spirit Soother'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Check if hp <= 6. If so, increase damage and heal
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        heal = 2
        if charactor.hp <= 6:
            self.damage = 5
            heal = 3
        damage_action = self.attack_opposite_active(match, self.damage, 
                                                    self.damage_type)
        heal_action = self.attack_self(match, -heal)
        damage_action.damage_value_list += heal_action.damage_value_list
        self.damage = 4
        return [
            self.charge_self(-3),
            damage_action,
        ]

# Talents


class SanguineRouge_3_7(SkillTalent):
    name: Literal['Sanguine Rouge']
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Hu Tao'] = 'Hu Tao'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2
    )
    skill: Literal['Guide to Afterlife'] = 'Guide to Afterlife'

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self use damage skill
            return value
        if value.damage_elemental_type != DamageElementalType.PYRO:
            # not pyro damage
            return value
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp > 6:
            # hp > 6
            return value
        # increase damage
        value.damage += 1
        return value


# charactor base


class HuTao_3_7(CharactorBase):
    name: Literal['Hu Tao']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | GuideToAfterlife | SpiritSoother
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Secret Spear of Wangsheng',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GuideToAfterlife(),
            SpiritSoother()
        ]


register_class(HuTao_3_7 | SanguineRouge_3_7)
