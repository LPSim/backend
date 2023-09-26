from typing import List, Literal
from ..cryo.fatui_cryo_cicin_mage import FatuiCryoCicinMage as FCC_4_1
from ..cryo.fatui_cryo_cicin_mage import CryoCicins as CC_4_1
from ..cryo.fatui_cryo_cicin_mage import MistySummons as MS_4_1
from ..cryo.fatui_cryo_cicin_mage import CicinIcicle, BlizzardBranchBlossom


class CryoCicins_3_7(CC_4_1):
    desc: str = (
        'End Phase: Deal 1 Cryo DMG. (Can stack. Max 3 stacks.) '
        'After Fatui Cryo Cicin Mage performs a Normal Attack: This card '
        'gains 1 Usage(s). After your character takes Elemental Reaction DMG: '
        'This card loses 1 Usage(s).'
    )
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
