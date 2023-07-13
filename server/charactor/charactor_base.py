"""
Base class of charactors. Each charactor should have its own file, the file
contains the charactor class, talent class, talent card class, skill classes.
DO NOT implement status, summons, weapons, artifacts, etc. in this file, which
will break the import loop.
"""


from typing import List, Literal
from ..consts import (
    ObjectType, WeaponType, ElementType, FactionType
)
from ..object_base import (
    ObjectBase, SkillBase, ArtifactBase, WeaponBase, TalentBase
)
from ..status import CharactorStatus


class CharactorBase(ObjectBase):
    """
    Base class of charactors.
    """
    name: str
    type: Literal[ObjectType.CHARACTOR] = ObjectType.CHARACTOR
    element: ElementType
    hp: int
    max_hp: int
    charge: int
    max_charge: int
    skills: List[SkillBase]

    # labels
    faction: List[FactionType]
    weapon_type: WeaponType

    # charactor status
    weapon: WeaponBase | None = None
    artifact: ArtifactBase | None = None
    talent: TalentBase | None = None
    status: List[CharactorStatus] = []

    @property
    def is_defeated(self):
        return self.hp == 0
