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
    version: str
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
    element_application: List[ElementType] = []
    is_alive: bool = True

    @property
    def is_defeated(self):
        return not self.is_alive

    def get_object_lists(self) -> List[ObjectBase]:
        """
        Get all objects in the match by `self.table.get_object_lists`. 
        The order of objects should follow the game rule. The rules are:
        1. objects of `self.current_player` goes first
        2. objects belongs to charactor goes first
            2.1. active charactor first, otherwise the default order.
            2.2. for one charactor, order is weapon, artifact, talent, status.
            2.3. for status, order is their index in status list, i.e. 
                generated time.
        3. for other objects, order is: summon, support, hand, dice, deck.
            3.1. all other objects in same region are sorted by their index in
                the list.
        """
        result: List[ObjectBase] = [self]
        if self.weapon is not None:
            result.append(self.weapon)
        if self.artifact is not None:
            result.append(self.artifact)
        if self.talent is not None:
            result.append(self.talent)
        result += self.status
        return result
