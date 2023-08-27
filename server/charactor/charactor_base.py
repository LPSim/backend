"""
Base class of charactors. Each charactor should have its own file, the file
contains the charactor class, talent class, talent card class, skill classes.
DO NOT implement status, summons, weapons, artifacts, etc. in this file, which
will break the import loop.
"""


from typing import List, Literal, Any
from ..consts import (
    ObjectType, WeaponType, ElementType, FactionType, ObjectPositionType,
    DiceCostLabels
)
from ..object_base import (
    ObjectBase, SkillBase, WeaponBase, CardBase
)
from ..struct import ObjectPosition, CardActionTarget
from ..status import CharactorStatus
from ..card.equipment.artifact import Artifacts
from ..action import (
    CombatActionAction, MoveObjectAction, RemoveObjectAction, Actions
)


class TalentBase(CardBase):
    """
    Base class of talents. Note almost all talents are skills, and will receive
    cost decrease from other objects.
    """
    name: str
    charactor_name: str
    type: Literal[ObjectType.TALENT] = ObjectType.TALENT
    cost_label: int = DiceCostLabels.CARD.value | DiceCostLabels.TALENT.value

    def is_valid(self, match: Any) -> bool:
        """
        Only corresponding charactor is active charactor can equip this card.
        """
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            return False
        table = match.player_tables[self.position.player_id]
        return (table.charactors[table.active_charactor_id].name
                == self.charactor_name)

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        """
        For most talent cards, can quip only on active charactor, so no need
        to specify targets.
        """
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[Actions]:
        """
        Act the talent. will place it into talent area.
        When other talent is equipped, remove the old one.
        For subclasses, inherit this and add other actions (e.g. trigger
        correcponding skills)
        """
        assert target is None
        ret: List[Actions] = []
        table = match.player_tables[self.position.player_id]
        charactor = table.charactors[table.active_charactor_id]
        # check if need to remove current talent
        if charactor.talent is not None:
            ret.append(RemoveObjectAction(
                object_position = charactor.talent.position,
                object_id = charactor.talent.id,
            ))
        ret.append(MoveObjectAction(
            object_position = self.position,
            object_id = self.id,
            target_position = charactor.position.copy(deep = True),
        ))
        return ret


class SkillTalent(TalentBase):
    """
    Talents that trigger skills. They will get skill as input, which is
    saved as a private variable.
    """

    skill: SkillBase

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[Actions]:
        ret = super().get_actions(target, match)
        self.skill.position = self.position
        ret += self.skill.get_actions(match)
        # use cards are quick actions, but equip talent card will use skills,
        # so should add CombatActionAction.
        ret.append(CombatActionAction(
            action_type = 'SKILL',
            position = self.position.copy(deep = True)
        ))
        return ret


class CharactorBase(ObjectBase):
    """
    Base class of charactors.
    """
    name: str
    desc: str
    version: str
    type: Literal[ObjectType.CHARACTOR] = ObjectType.CHARACTOR
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        charactor_id = -1,
        area = ObjectPositionType.INVALID
    )

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
    artifact: Artifacts | None = None
    talent: TalentBase | None = None
    status: List[CharactorStatus] = []
    element_application: List[ElementType] = []
    is_alive: bool = True

    @property
    def is_defeated(self) -> bool:
        return not self.is_alive

    @property
    def is_stunned(self) -> bool:
        """
        Check if the charactor is stunned.
        """
        stun_status_names = [
            'Frozen',
            'Petrification',
            'Mist Bubble',
            'Stun',
        ]
        for status in self.status:
            if status.name in stun_status_names:
                return True
        return False

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
