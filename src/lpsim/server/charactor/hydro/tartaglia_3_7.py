from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import ElementalSkillBase, PhysicalNormalAttackBase

from ...action import Actions

from ...consts import DamageElementalType, DieColor

from ...struct import Cost

from .tartaglia_4_1 import (
    HavocObliteration as HO_4_1,
    TideWithholder as TW_4_1,
    Tartaglia_4_1 as Tartaglia_4_1,
    AbyssalMayhemHydrospout_4_1 as AMH_4_1,
)


# Skills


class FoulLegacyRagingTide(ElementalSkillBase):
    name: Literal['Foul Legacy: Raging Tide'] = 'Foul Legacy: Raging Tide'
    version: Literal['3.7'] = '3.7' 
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object then attack
        """
        return [
            self.create_charactor_status(
                'Melee Stance',
                { 'version': self.version }
            ),
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.charge_self(1),
        ]


class HavocObliteration(HO_4_1):
    name: Literal['Havoc: Obliteration'] = 'Havoc: Obliteration'
    version: Literal['3.7'] = '3.7' 
    ranged_damage: int = 4


class TideWithholder(TW_4_1):
    version: Literal['3.7'] = '3.7'


# Talents


class AbyssalMayhemHydrospout_3_7(AMH_4_1):
    version: Literal['3.7']
    only_active_charactor: bool = False
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
    )


# charactor base


class Tartaglia_3_7(Tartaglia_4_1):
    name: Literal['Tartaglia']
    version: Literal['3.7']
    skills: List[
        PhysicalNormalAttackBase | FoulLegacyRagingTide
        | HavocObliteration | TideWithholder
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Cutting Torrent',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            FoulLegacyRagingTide(),
            HavocObliteration(),
            TideWithholder(),
        ]


register_class(Tartaglia_3_7 | AbyssalMayhemHydrospout_3_7)
