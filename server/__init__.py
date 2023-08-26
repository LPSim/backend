from .summon import Summons as OtherSummons
from .charactor import Charactors  # noqa: F401
from .status import CharactorStatus, TeamStatus  # noqa: F401
from .card import Cards as OtherCards
from .card.support import Supports  # noqa: F401


# For summons and cards, some will implement in charactor files.
# For status, it is impossible, so no need to collect from other folder.
Summons = OtherSummons | OtherSummons
Cards = OtherCards | OtherCards
