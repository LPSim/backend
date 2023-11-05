from typing import List, Literal
from ..old_version.yanfei_3_8 import (
    DoneDeal, SealOfApproval, Yanfei_3_8, RightOfFinalInterpretation_3_8, 
    SignedEdict as SE_3_8
)


class SignedEdict(SE_3_8):
    status_desc: str = (
        'When the character uses a Charged Attack: Damage dealt +2. '
        '(Can stack, max 2)'
    )
    max_usage: int = 2
    version: Literal['4.2'] = '4.2'


class RightOfFinalInterpretation(RightOfFinalInterpretation_3_8):
    """
    Draw card action is performed by Scarlet Seal.
    """
    desc: str = (
        'Combat Action: When your active character is Yanfei, equip this '
        'card. After Yanfei equips this card, immediately use Seal of '
        'Approval once. When Yanfei uses a Charged Attack with this card '
        'equipped: Deal +1 DMG to enemies with 6 or less HP.'
        'If Scarlet Seal is triggered, then draw 1 card after the skill '
        'finishes calculating.'
    )
    version: Literal['4.2'] = '4.2'
    draw_card: bool = True


class Yanfei(Yanfei_3_8):
    version: Literal['4.2'] = '4.2'
    talent: RightOfFinalInterpretation | None = None
    skills: List[SealOfApproval | SignedEdict | DoneDeal] = [] 

    def _init_skills(self) -> None:
        self.skills = [
            SealOfApproval(),
            SignedEdict(),
            DoneDeal()
        ]
