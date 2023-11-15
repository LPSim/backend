from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import DamageIncreaseValue

from ...summon.base import AttackerSummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, SkillType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class GardenOfPurity_3_6(AttackerSummonBase):
    name: Literal['Garden of Purity'] = 'Garden of Purity'
    version: Literal['3.6'] = '3.6'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            assert mode == 'REAL'
            value.damage += 1
        return value


# Skills


class KamisatoArtKyouka(ElementalSkillBase):
    name: Literal['Kamisato Art: Kyouka'] = 'Kamisato Art: Kyouka'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_charactor_status(
                'Takimeguri Kanka',
                {
                    'usage': 3,
                    'max_usage': 3
                }
            ),
        ]


class KamisatoArtSuiyuu(ElementalBurstBase):
    name: Literal['Kamisato Art: Suiyuu'] = 'Kamisato Art: Suiyuu'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Garden of Purity')
        ]


# Talents


class KyoukaFuushi_3_6(SkillTalent):
    name: Literal['Kyouka Fuushi']
    version: Literal['3.6'] = '3.6'
    charactor_name: Literal['Kamisato Ayato'] = 'Kamisato Ayato'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: Literal['Kamisato Art: Kyouka'] = 'Kamisato Art: Kyouka'


# charactor base


class KamisatoAyato_4_1(CharactorBase):
    name: Literal['Kamisato Ayato']
    version: Literal['4.1'] = '4.1'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | KamisatoArtKyouka | KamisatoArtSuiyuu
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Kamisato Art: Marobashi',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            KamisatoArtKyouka(),
            KamisatoArtSuiyuu(),
        ]


register_class(KamisatoAyato_4_1 | KyoukaFuushi_3_6 | GardenOfPurity_3_6)
