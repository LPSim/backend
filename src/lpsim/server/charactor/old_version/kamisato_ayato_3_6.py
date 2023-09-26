from typing import List, Literal

from ..charactor_base import PhysicalNormalAttackBase
from ...struct import Cost
from ...consts import DieColor
from ..hydro.kamisato_ayato import KamisatoAyato as KA_4_1
from ..hydro.kamisato_ayato import KamisatoArtSuiyuu as KAS_4_1
from ..hydro.kamisato_ayato import KamisatoArtKyouka


class KamisatoArtSuiyuu(KAS_4_1):
    desc: str = '''Deals 3 Hydro DMG, summons 1 Garden of Purity.'''
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
