from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...status.team_status.base import ShieldTeamStatus

from ...status.charactor_status.base import ShieldCharactorStatus

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageIncreaseValue

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class StoneStele_3_7(AttackerSummonBase):
    name: Literal['Stone Stele'] = 'Stone Stele'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.GEO
    damage: int = 1


# Skills


class DominusLapidis(ElementalSkillBase):
    name: Literal['Dominus Lapidis'] = 'Dominus Lapidis'
    damage: int = 1
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
            self.create_summon('Stone Stele')
        ]


class DominusLapidisStrikingStone(ElementalSkillBase):
    name: Literal[
        'Dominus Lapidis: Striking Stone'] = 'Dominus Lapidis: Striking Stone'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 5
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('Stone Stele'),
            self.create_team_status('Jade Shield')
        ]


class PlanetBefall(ElementalBurstBase):
    name: Literal['Planet Befall'] = 'Planet Befall'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack target, and create status for target
        """
        return super().get_actions(match) + [
            self.create_opposite_charactor_status(
                match, 'Petrification', {}
            )
        ]


# Talents


class DominanceOfEarth_3_7(SkillTalent):
    name: Literal['Dominance of Earth']
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Zhongli'] = 'Zhongli'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 5
    )
    skill: Literal[
        'Dominus Lapidis: Striking Stone'
    ] = 'Dominus Lapidis: Striking Stone'

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['REAL', 'TEST']
    ) -> DamageIncreaseValue:
        """
        If active charactor has shield, or team status has shield, increase
        geo summon damage
        """
        if (
            self.position.area != ObjectPositionType.CHARACTOR
            or value.position.player_idx != self.position.player_idx
            or value.position.area != ObjectPositionType.SUMMON
            or value.damage_type != DamageType.DAMAGE
            or value.damage_elemental_type != DamageElementalType.GEO
        ):
            # not equipped, or self summon, or not geo damage
            return value
        table = match.player_tables[self.position.player_idx]
        team_status = table.team_status
        have_shield = False
        team_status = table.team_status
        for status in team_status:
            if issubclass(type(status), ShieldTeamStatus):
                have_shield = True
        if not have_shield:
            # no shield team status, check charactor status
            active_charactor = table.get_active_charactor()
            for status in active_charactor.status:
                if issubclass(type(status), ShieldCharactorStatus):
                    have_shield = True
        if not have_shield:
            # no shield
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


# charactor base


class Zhongli_3_7(CharactorBase):
    name: Literal['Zhongli']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | DominusLapidis 
        | DominusLapidisStrikingStone | PlanetBefall
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Rain of Stone',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            DominusLapidis(),
            DominusLapidisStrikingStone(),
            PlanetBefall()
        ]


register_class(Zhongli_3_7 | DominanceOfEarth_3_7 | StoneStele_3_7)
