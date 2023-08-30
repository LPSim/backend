"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. CardBase are defined here because like ObjectBase, they are used 
in many other places. Other objects are defined in their own files.
"""


import time
import random
from utils import BaseModel
from typing import List, Literal, Any
from .action import ActionBase, ActionTypes
from .consts import ObjectType, WeaponType, ObjectPositionType, CostLabels
from .modifiable_values import ModifiableValueTypes
from .struct import (
    ObjectPosition, Cost, CardActionTarget
)


used_object_ids = set()


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    position: ObjectPosition
    id: int = 0

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # check event handler name valid
        for k in dir(self):
            if k[:14] == 'event_handler_':
                k = k[14:]
                try:
                    k = ActionTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid event handler name: {k}')
            if k[:15] == 'value_modifier_':
                k = k[15:]
                try:
                    k = ModifiableValueTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid value modifier name: {k}')
        # if id is zero, generate a new id
        if self.id == 0:
            while True:
                self.id = (
                    int(time.time() % 86400 * 1000000) 
                    * 1024 + random.randint(0, 1023)
                )
                if self.id not in used_object_ids:
                    break
        used_object_ids.add(self.id)


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: str
    desc: str
    type: Literal[ObjectType.CARD, ObjectType.WEAPON, ObjectType.ARTIFACT,
                  ObjectType.TALENT, ObjectType.SUMMON,
                  ObjectType.SUPPORT] = ObjectType.CARD
    version: str
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID
    )
    cost: Cost
    cost_label: int = CostLabels.CARD.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set cost label into cost
        self.cost.label = self.cost_label
        assert self.cost.original_value is None

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        """
        Get the targets of the card.
        """
        raise NotImplementedError

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[ActionBase]:
        """
        Act the card. It will return a list of actions.

        Arguments:
            args (CardActionArguments | None): The arguments of the action.
                for cards that do not need to specify target, args is None.
            match (Any): The match object.
        """
        raise NotImplementedError()

    def is_valid(self, match: Any) -> bool:
        """
        Check if the card can be used. Note that this function will not check
        the cost of the card.
        """
        return True


class WeaponBase(CardBase):
    """
    Base class of weapons.
    """
    name: str
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    cost_label: int = CostLabels.CARD.value | CostLabels.WEAPON.value
    weapon_type: WeaponType
