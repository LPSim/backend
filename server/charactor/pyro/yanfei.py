from typing import Any, List, Literal

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
    desc: str = (
        'Deals 3 Pyro DMG and attaches Scarlet Seal to this character.'
    )
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
        return super().get_actions(match) + [
            self.create_charactor_status('Scarlet Seal')
        ]


class DoneDeal(ElementalBurstBase):
    name: Literal['Done Deal'] = 'Done Deal'
    desc: str = (
        'Deals 3 Pyro DMG, attaches Scarlet Seal and Brilliance to this '
        'character.'
    )
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


class RightOfFinalInterpretation(SkillTalent):
    name: Literal['Right of Final Interpretation']
    desc: str = (
        'Combat Action: When your active character is Yanfei, equip this '
        'card. After Yanfei equips this card, immediately use Seal of '
        'Approval once. When Yanfei uses a Charged Attack with this card '
        'equipped: Deal +1 DMG to enemies with 6 or less HP.'
    )
    version: Literal['3.8'] = '3.8'
    charactor_name: Literal['Yanfei'] = 'Yanfei'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 1,
        any_dice_number = 2,
    )
    skill: SealOfApproval = SealOfApproval()

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


class Yanfei(CharactorBase):
    name: Literal['Yanfei']
    version: Literal['3.8'] = '3.8'
    desc: str = '''Wise Innocence: Yanfei'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        SealOfApproval | SignedEdict | DoneDeal
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: RightOfFinalInterpretation | None = None

    def _init_skills(self) -> None:
        self.skills = [
            SealOfApproval(),
            SignedEdict(),
            DoneDeal()
        ]
