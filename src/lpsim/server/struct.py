from typing import List, Any, Literal

from .query import satisfy

from ..utils import BaseModel
from .consts import ObjectPositionType, DieColor


class ObjectPosition(BaseModel):
    """
    Position of an object in the game table, which will be set at initializing
    or updated when its position changes. Current change event: card go from
    deck to hand, from hand to deck, from hand to character, from character to
    hand, from character to character, from hand to support, from support to
    support.

    Note the index of the object is not included (n-th summon from player 1's
    sommon lists) as it will change when some action triggered, for example
    RemoveSummonAction. For these actions, we will use the id of the object
    to identify.

    Position is mainly used for objects to decide whether to respond events.

    It is immutable.

    Args:
        player_idx (int): The player index of the object.
        character_idx (int): The character index of the object. If it is not
            on character, set to -1.
        area (ObjectPositionType): The area of the object.
        id (int): The id of the object. If it is not on table, set to -1.
            If it represents SYSTEM, set to 0.
    """

    player_idx: int
    character_idx: int = -1
    area: ObjectPositionType
    id: int

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)
        if self.area in [ObjectPositionType.INVALID, ObjectPositionType.SYSTEM]:
            # invalid or system position, do not check other attributes
            return
        # check player_idx is propoerly set
        assert self.player_idx >= 0, "player_idx should be non-negative."
        # check character_idx is properly set
        if self.area in [
            ObjectPositionType.CHARACTER_STATUS,
            ObjectPositionType.SKILL,
            ObjectPositionType.CHARACTER,
        ]:
            assert self.character_idx >= 0, "character_idx should be non-negative."

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Override __setattr__ to make it immutable.
        """
        raise AttributeError("ObjectPosition is immutable.")

    def __delattr__(self, name: str) -> None:
        """
        Override __delattr__ to make it immutable.
        """
        raise AttributeError("ObjectPosition is immutable.")

    def set_id(self, id: int) -> "ObjectPosition":
        """
        Return a new ObjectPosition with the id set.
        """
        return ObjectPosition(
            player_idx=self.player_idx,
            character_idx=self.character_idx,
            area=self.area,
            id=id,
        )

    def set_area(self, area: ObjectPositionType) -> "ObjectPosition":
        """
        Return a new ObjectPosition with the area set.
        """
        return ObjectPosition(
            player_idx=self.player_idx,
            character_idx=self.character_idx,
            area=area,
            id=self.id,
        )

    def copy(self) -> "ObjectPosition":
        """
        As it is a immutable object, it is no need to copy.
        """
        raise AssertionError("ObjectPosition is immutable.")

    def check_position_valid(
        self,
        target_position: "ObjectPosition",
        match: Any,
        player_idx_same: bool | None = None,
        character_idx_same: bool | None = None,
        area_same: bool | None = None,
        id_same: bool | None = None,
        source_area: ObjectPositionType | None = None,
        target_area: ObjectPositionType | None = None,
        source_is_active_character: bool | None = None,
        target_is_active_character: bool | None = None,
    ) -> bool:
        """
        @deprecated This function is deprecated. Use `self.satisfy` instead.

        Based on this position, target position and constraints, give whether
        two position relations fit the constraints.
        """
        if player_idx_same is not None:
            if player_idx_same != (self.player_idx == target_position.player_idx):
                return False
        if character_idx_same is not None:
            if character_idx_same != (
                self.character_idx == target_position.character_idx
            ):
                return False
        if area_same is not None:
            if area_same != (self.area == target_position.area):
                return False
        if id_same is not None:
            if id_same != (self.id == target_position.id):
                return False
        if source_area is not None:
            if self.area != source_area:
                return False
        if target_area is not None:
            if target_position.area != target_area:
                return False
        if source_is_active_character is not None:
            cidx = match.player_tables[self.player_idx].active_character_idx
            return source_is_active_character == (self.character_idx == cidx)
        if target_is_active_character is not None:
            cidx = match.player_tables[target_position.player_idx].active_character_idx
            return target_is_active_character == (target_position.character_idx == cidx)
        return True

    def satisfy(
        self,
        command: str,
        target: "ObjectPosition | None" = None,
        match: Any | None = None,
    ) -> bool:
        """
        Check whether object position satisfies the command.
        Optionally receives target `ObjectPosition` and match. If they are not input,
        related command string will raise error.

        Command formats are:
        - `source / target` to select one object position, or `both` to compare between
            two positions
        - if one position selected: `[pidx=? / cidx=? / area=? / active=(true|false)]`
            to check if position fulfills the situation. for area names, they are case
            insensitive. can use multiple times, and all of them should pass.
        - if two position selected (i.e. `both`), `[(pidx|cidx|area|id)=(same|diff)]`
            to compare two positions are same or not. can use multiple times, and all of
            them should pass.
        - `and` to make multiple checks. All check should pass.

        samples:
        - `source area=support` is this object placed to support
        - `source area=character and target area=skill and both pidx=same cidx=same` is
            this object equipped to a character, and target object is skill of this
            character
        - `both pidx=same and source area=hand and target area=skill` this object in
            hand and target object is this player use skill
        """
        return satisfy(self, command, target, match)

    def not_satisfy(
        self,
        command: str,
        target: "ObjectPosition | None" = None,
        match: Any | None = None,
    ) -> bool:
        """
        Check whether object position not satisfies the command.
        Optionally receives target `ObjectPosition` and match. If they are not input,
        related command string will raise error.

        Command formats are the same as `satisfy`. The result is just the opposite
        of `satisfy`.
        """
        return not self.satisfy(command, target, match)


class MultipleObjectPosition(BaseModel):
    positions: List[ObjectPosition]


class Cost(BaseModel):
    """
    The cost, which is used to define original costs of objects.
    When perform cost, should convert into CostValue.
    """

    label: int = 0
    elemental_dice_number: int = 0
    elemental_dice_color: DieColor | None = None
    same_dice_number: int = 0
    any_dice_number: int = 0
    omni_dice_number: int = 0
    charge: int = 0
    arcane_legend: bool = False
    original_value: Any | None = None

    def copy(self, *argv, **kwargs) -> "Cost":
        """
        Do not support extra args. When perform copy, create new
        instance instead of copy.
        """
        assert len(argv) == 0 and len(kwargs) == 0, "Do not support extra args"
        ori_copy = None
        if self.original_value is not None:  # pragma: no cover
            ori_copy = self.original_value.copy()
        return Cost(
            label=self.label,
            elemental_dice_number=self.elemental_dice_number,
            elemental_dice_color=self.elemental_dice_color,
            same_dice_number=self.same_dice_number,
            any_dice_number=self.any_dice_number,
            omni_dice_number=self.omni_dice_number,
            charge=self.charge,
            arcane_legend=self.arcane_legend,
            original_value=ori_copy,
        )

    @property
    def total_dice_cost(self) -> int:
        """
        Return the total dice cost.
        """
        return (
            self.elemental_dice_number
            + self.same_dice_number
            + self.any_dice_number
            + self.omni_dice_number
        )

    def decrease_cost(self, dice_color: DieColor | None) -> bool:
        """
        Decrease the cost by 1 dice of the given color in-place.

        Return True if decrease successfully, False if not.

        Args:
            dice_color (DieColor | None): The dice color to be decreased.
                If None, decrease same or any dice; Otherwise, decrease
                elemental or any dice.
        """
        assert dice_color != DieColor.OMNI, "Omni dice is not supported yet."
        if dice_color is None:
            # decrease same or any dice
            if self.same_dice_number > 0:
                self.same_dice_number -= 1
                return True
            if self.any_dice_number > 0:
                self.any_dice_number -= 1
                return True
            return False
        # decrease elemental or any dice
        if self.elemental_dice_color == dice_color and self.elemental_dice_number > 0:
            self.elemental_dice_number -= 1
            return True
        if self.any_dice_number > 0:
            self.any_dice_number -= 1
            return True
        return False

    def is_valid(
        self, dice_colors: List[DieColor], charge: int, arcane_legend: bool, strict=True
    ) -> bool:
        """
        Check if dice colors matches the dice cost value.

        Args:
            dice_colors (List[DieColor]): The dice colors to be checked.
            charge (int): The charges to be checked.
            strict (bool): If True, the dice colors must match the dice cost
                value strictly. If False, the dice colors can be more than the
                cost. Note charges always match unstictly.
        """
        # first charge check
        if charge < self.charge:
            return False
        # then arcane legend check
        if self.arcane_legend and not arcane_legend:
            return False

        # then dice number check, no minus
        assert self.elemental_dice_number >= 0
        assert self.same_dice_number >= 0
        assert self.any_dice_number >= 0
        assert self.omni_dice_number >= 0

        # then dice check
        assert self.omni_dice_number == 0, "Omni dice is not supported yet."
        if self.same_dice_number > 0:
            assert (
                self.elemental_dice_number == 0 and self.any_dice_number == 0
            ), "Same dice and elemental/any dice cannot be both used now."
        assert not (
            self.elemental_dice_number > 0 and self.elemental_dice_color is None
        ), "Elemental dice number and color should be both set."
        if strict:
            if len(dice_colors) != (
                self.elemental_dice_number
                + self.same_dice_number
                + self.any_dice_number
                + self.omni_dice_number
            ):
                return False  # dice number not match
        else:
            if len(dice_colors) < (
                self.elemental_dice_number
                + self.same_dice_number
                + self.any_dice_number
                + self.omni_dice_number
            ):
                return False  # dice number not enough
        d = {}
        for color in dice_colors:
            d[color] = d.get(color, 0) + 1
        omni_num = d.get(DieColor.OMNI, 0)
        if self.elemental_dice_number > 0:
            ele_num = d.get(self.elemental_dice_color, 0)
            if ele_num + omni_num < self.elemental_dice_number:
                return False  # elemental dice not enough
        if self.same_dice_number > 0:
            if DieColor.OMNI not in d:
                d[DieColor.OMNI] = 0
            if d[DieColor.OMNI] >= self.same_dice_number:
                return True
            success = False
            for color, same_num in d.items():
                if color == DieColor.OMNI:
                    continue
                if same_num + omni_num >= self.same_dice_number:
                    success = True
                    break
            return success
        return True


class DeckRestriction(BaseModel):
    """
    Deck restriction to add one card into deck
    """

    type: Literal["NONE", "CHARACTER", "FACTION", "ELEMENT"]
    name: str
    number: int
