from typing import List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase
from ...struct import Cost
from ...consts import DieColor
from .kamisato_ayato_4_1 import KamisatoAyato_4_1 as KA_4_1
from .kamisato_ayato_4_1 import KamisatoArtSuiyuu as KAS_4_1
from .kamisato_ayato_4_1 import KamisatoArtKyouka


class KamisatoArtSuiyuu(KAS_4_1):
    damage: int = 3
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3
    )


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
