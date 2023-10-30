from typing import Literal


from ...consts import IconType

from .base import RoundCharactorStatus
from .cryo_charactors import Grimheart as G_3_8
from .foods import MintyMeatRolls as MMR_3_4
from .hydro_charactors import RangedStance as RS_4_1, MeleeStance as MS_4_1
from .hydro_charactors import Riptide as Riptide_4_1


class Grimheart_3_5(G_3_8):
    version: Literal['3.5']
    damage: int = 2


class MintyMeatRolls_3_3(MMR_3_4):
    desc: str = (
        "During this Round, the target character's Normal Attacks cost "
        "less 1 Unaligned Element."
    )
    version: Literal['3.3']
    decrease_usage: int = 999


class Riptide_3_7(Riptide_4_1, RoundCharactorStatus):
    """
    This status will not deal damages directly, and defeat-regenerate is 
    handled by system handler, which is created by Tartaglia'is passive skill
    when game starts.
    """
    name: Literal['Riptide'] = 'Riptide'
    desc: str = (
        'When the character to which this is attached is defeated: Apply '
        'Riptide to active character. '
        'When Tartaglia is in Melee Stance, he will deal additional DMG when '
        'attacking the character to which this is attached.'
    )
    version: Literal['3.7']
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS


class RangedStance_3_7(RS_4_1):
    version: Literal['3.7']


class MeleeStance_3_7(MS_4_1):
    version: Literal['3.7']


OldVersionCharactorStatus = (
    Riptide_3_7 | RangedStance_3_7 | MeleeStance_3_7

    | Grimheart_3_5 

    | MintyMeatRolls_3_3
)
