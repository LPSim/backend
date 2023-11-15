from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import AttackerSummonBase

from ...modifiable_values import CostValue, DamageIncreaseValue
from ...event import RoundPrepareEventArguments

from ...action import Actions
from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class SolarIsotoma_4_0(AttackerSummonBase):
    name: Literal['Solar Isotoma'] = 'Solar Isotoma'
    version: Literal['4.0'] = '4.0'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.GEO
    damage: int = 1

    attack_cost_decrease_usage: int = 1

    def renew(self, match: Any) -> None:
        super().renew(match)
        self.attack_cost_decrease_usage = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, reset usage
        """
        self.attack_cost_decrease_usage = 1
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        if self use plunging attack and has usage, decrease cost
        """
        if (
            self.attack_cost_decrease_usage > 0
            and value.cost.label & CostLabels.PLUNGING_ATTACK > 0
            and value.position.player_idx == self.position.player_idx
        ):
            # is self and has usage and plunging attack
            if value.cost.decrease_cost(None):
                if mode == 'REAL':
                    self.attack_cost_decrease_usage -= 1
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['REAL', 'TEST']
    ) -> DamageIncreaseValue:
        """
        If has albedo equip talent, increase plunging attack by 1
        """
        if value.position.player_idx != self.position.player_idx:
            # not self
            return value
        found_talent_albedo = False
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if charactor.name == 'Albedo' and charactor.talent is not None:
                found_talent_albedo = True
                break
        if not found_talent_albedo:
            # not found
            return value
        if (
            value.cost.label & CostLabels.NORMAL_ATTACK.value > 0
            and match.player_tables[self.position.player_idx].plunge_satisfied
        ):
            # plunging attack
            assert mode == 'REAL'
            value.damage += 1
        return value


# Skills


class AbiogenesisSolarIsotoma(ElementalSkillBase):
    name: Literal['Abiogenesis: Solar Isotoma'] = 'Abiogenesis: Solar Isotoma'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [
            self.create_summon('Solar Isotoma'),
            self.charge_self(1),
        ]


class RiteOfProgenitureTectonicTide(ElementalBurstBase):
    name: Literal[
        'Rite of Progeniture: Tectonic Tide'
    ] = 'Rite of Progeniture: Tectonic Tide'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Check if Solar Isotoma exists. If so, change self.damage to 8.
        """
        summons = match.player_tables[self.position.player_idx].summons
        isotoma_exist: bool = False
        for s in summons:
            if s.name == 'Solar Isotoma':
                isotoma_exist = True
                break
        if isotoma_exist:
            # temporary change damage to 6
            self.damage = 6
        ret = super().get_actions(match)
        self.damage = 4
        return ret


# Talents


class DescentOfDivinity_4_0(SkillTalent):
    name: Literal['Descent of Divinity']
    version: Literal['4.0'] = '4.0'
    charactor_name: Literal['Albedo'] = 'Albedo'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3
    )
    skill: Literal['Abiogenesis: Solar Isotoma'] = 'Abiogenesis: Solar Isotoma'


# charactor base


class Albedo_4_0(CharactorBase):
    name: Literal['Albedo']
    version: Literal['4.0'] = '4.0'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | AbiogenesisSolarIsotoma 
        | RiteOfProgenitureTectonicTide
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework - Weiss',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            AbiogenesisSolarIsotoma(),
            RiteOfProgenitureTectonicTide()
        ]


register_class(Albedo_4_0 | DescentOfDivinity_4_0 | SolarIsotoma_4_0)
