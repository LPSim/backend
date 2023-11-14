from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import DamageIncreaseValue

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)
# Skills


class SealOfApproval(ElementalNormalAttackBase):
    name: Literal['Seal of Approval'] = 'Seal of Approval'
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = ElementalNormalAttackBase.get_cost(ElementType.PYRO)


class SignedEdict(ElementalSkillBase):
    name: Literal['Signed Edict'] = 'Signed Edict'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )
    version: Literal['3.8'] = '3.8'

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_charactor_status('Scarlet Seal', {
                'version': self.version,
            })
        ]


class DoneDeal(ElementalBurstBase):
    name: Literal['Done Deal'] = 'Done Deal'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_charactor_status('Scarlet Seal'),
            self.create_charactor_status('Brilliance'),
        ]


# Talents


class RightOfFinalInterpretation_3_8(SkillTalent):
    name: Literal['Right of Final Interpretation']
    version: Literal['3.8'] = '3.8'
    charactor_name: Literal['Yanfei'] = 'Yanfei'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 1,
        any_dice_number = 2,
    )
    skill: Literal['Seal of Approval'] = 'Seal of Approval'
    draw_card: bool = False

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if not self.position.area == ObjectPositionType.CHARACTOR:
            # not equiped
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not self use normal attack
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charge attack
            return value
        if value.damage_from_element_reaction:  # pragma: no cover
            # damage from element reaction
            return value
        target = match.get_object(value.target_position)
        if target.hp > 6:
            # target hp > 6
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


# charactor base


class Yanfei_3_8(CharactorBase):
    name: Literal['Yanfei']
    version: Literal['3.8'] = '3.8'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[SealOfApproval | SignedEdict | DoneDeal] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            SealOfApproval(),
            SignedEdict(),
            DoneDeal()
        ]


register_class(Yanfei_3_8 | RightOfFinalInterpretation_3_8)
