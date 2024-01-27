from typing import List, Literal

from ....utils.class_registry import register_class
from .yanfei_3_8 import (
    DoneDeal, SealOfApproval, Yanfei_3_8, RightOfFinalInterpretation_3_8, 
    SignedEdict as SE_3_8
)


class SignedEdict(SE_3_8):
    max_usage: int = 2
    version: Literal['4.2'] = '4.2'


class RightOfFinalInterpretation_4_2(RightOfFinalInterpretation_3_8):
    """
    Draw card action is performed by Scarlet Seal.
    """
    version: Literal['4.2'] = '4.2'
    draw_card: bool = True


class Yanfei_4_2(Yanfei_3_8):
    version: Literal['4.2'] = '4.2'
    skills: List[SealOfApproval | SignedEdict | DoneDeal] = [] 

    def _init_skills(self) -> None:
        self.skills = [
            SealOfApproval(),
            SignedEdict(),
            DoneDeal()
        ]


register_class(Yanfei_4_2 | RightOfFinalInterpretation_4_2)
