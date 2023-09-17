from typing import Any, List, Literal
from ...action import Actions
from ..charactor_base import ElementalNormalAttackBase
from ..hydro.sangonomiya_kokomi import SangonomiyaKokomi as SK_3_6
from ..hydro.sangonomiya_kokomi import NereidsAscension as NA_3_6
from ..hydro.sangonomiya_kokomi import KuragesOath


class NereidsAscension(NA_3_6):
    desc: str = (
        'Deals 3 Hydro DMG. This character gains Ceremonial Garment.'
    )
    damage: int = 3

    def get_actions(self, match: Any) -> List[Actions]:
        """
        No healing
        """
        return super(NA_3_6, self).get_actions(match) + [
            self.create_charactor_status('Ceremonial Garment'),
        ]


class SangonomiyaKokomi_3_5(SK_3_6):
    version: Literal['3.5']
    skills: List[
        ElementalNormalAttackBase | KuragesOath | NereidsAscension
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'The Shape of Water',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            KuragesOath(),
            NereidsAscension(),
        ]
