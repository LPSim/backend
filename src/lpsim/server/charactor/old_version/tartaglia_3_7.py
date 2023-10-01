from typing import Any, List, Literal

from ..charactor_base import ElementalSkillBase, PhysicalNormalAttackBase

from ...action import Actions

from ...consts import DamageElementalType, DieColor

from ...struct import Cost

from ..hydro.tartaglia import (
    HavocObliteration as HO_4_1,
    TideWithholder as TW_4_1,
    Tartaglia as Tartaglia_4_1,
    AbyssalMayhemHydrospout as AMH_4_1,
)


# Skills


class FoulLegacyRagingTide(ElementalSkillBase):
    name: Literal['Foul Legacy: Raging Tide'] = 'Foul Legacy: Raging Tide'
    desc: str = '''Switches to Melee Stance and deals 2 Hydro DMG.'''
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
    desc: str = (
        'Performs different attacks based on the current stance that '
        'Tartaglia is in. Ranged Stance - Flash of Havoc: Deal 4 Hydro DMG, '
        'reclaim 2 Energy, and apply Riptide to the target character. '
        'Melee Stance - Light of Obliteration: Deal 7 Hydro DMG.'
    )
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
    talent: AbyssalMayhemHydrospout_3_7 | None = None

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
