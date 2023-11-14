from typing import List, Literal

from ....utils.class_registry import register_class
from .fatui_cryo_cicin_mage_4_1 import FatuiCryoCicinMage_4_1 as FCC_4_1
from .fatui_cryo_cicin_mage_4_1 import CryoCicins_4_1 as CC_4_1
from .fatui_cryo_cicin_mage_4_1 import MistySummons as MS_4_1
from .fatui_cryo_cicin_mage_4_1 import CicinIcicle, BlizzardBranchBlossom


class CryoCicins_3_7(CC_4_1):
    version: Literal['3.7'] = '3.7'
    decrease_only_self_damage: bool = False


class MistySummons(MS_4_1):
    version: Literal['3.7'] = '3.7'


class FatuiCryoCicinMage_3_7(FCC_4_1):
    version: Literal['3.7']
    skills: List[
        CicinIcicle | MistySummons | BlizzardBranchBlossom
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            CicinIcicle(),
            MistySummons(),
            BlizzardBranchBlossom(),
        ]


register_class(FatuiCryoCicinMage_3_7 | CryoCicins_3_7)
