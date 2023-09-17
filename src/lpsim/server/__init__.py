from .summon import Summons as OtherSummons
from .charactor import (  # noqa: F401
    Charactors, SummonsOfCharactors, CharactorTalents
)
from .status import CharactorStatus, TeamStatus  # noqa: F401
from .card import Cards as OtherCards
from .card.support import Supports  # noqa: F401


# For summons and cards, some will implement in charactor files.
# For status, it is impossible, so no need to collect from other folder.
Summons = OtherSummons | SummonsOfCharactors
Cards = OtherCards | CharactorTalents
