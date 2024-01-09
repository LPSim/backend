from typing import Any, List, Literal

from ...action import Actions

from ....utils.class_registry import register_class

from ..charactor_base import ElementalSkillBase, PhysicalNormalAttackBase
from ...struct import Cost
from ...consts import DamageElementalType, DieColor
from .kamisato_ayato_4_1 import KamisatoAyato_4_1 as KA_4_1
from .kamisato_ayato_4_1 import KamisatoArtSuiyuu as KAS_4_1


class KamisatoArtSuiyuu(KAS_4_1):
    damage: int = 3
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3
    )


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
        return super().get_actions(match, [
            self.create_charactor_status('Takimeguri Kanka'),
        ])


class KamisatoAyato_3_6(KA_4_1):
    version: Literal['3.6']
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | KamisatoArtKyouka | KamisatoArtSuiyuu
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Kamisato Art: Marobashi',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            KamisatoArtKyouka(),
            KamisatoArtSuiyuu(),
        ]


register_class(KamisatoAyato_3_6)
