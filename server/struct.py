from typing import List, Literal, Any

from utils import BaseModel
from .consts import (
    ObjectPositionType, DamageType, DamageElementalType,
    DieColor
)


class ObjectPosition(BaseModel):
    """
    Position of an object in the game table, which will be set at initializing
    or updated when its position changes. Current change event: card go from
    deck to hand, from hand to deck, from hand to charactor, from charactor to
    hand, from charactor to charactor, from hand to support, from support to 
    support.

    Note the index of the object is not included (n-th summon from player 1's
    sommon lists) as it will change when some action triggered, for example
    RemoveSummonAction. For these actions, we will use the id of the object
    to identify.

    Position is mainly used for objects to decide whether to respond events.

    Args:
        player_idx (int): The player index of the object.
        charactor_idx (int): The charactor index of the object. If it is not
            on charactor, set to -1.
        area (ObjectPositionType): The area of the object.
        id (int): The id of the object. If it is not on table, set to -1.
            If it represents SYSTEM, set to 0.
    """
    player_idx: int
    charactor_idx: int = -1
    area: ObjectPositionType
    id: int

    def check_position_valid(
        self, target_position: 'ObjectPosition', match: Any,
        player_idx_same: bool | None = None,
        charactor_idx_same: bool | None = None,
        area_same: bool | None = None,
        id_same: bool | None = None,
        source_area: ObjectPositionType | None = None,
        target_area: ObjectPositionType | None = None,
        source_is_active_charactor: bool | None = None,
        target_is_active_charactor: bool | None = None,
    ) -> bool:
        """
        Based on this position, target position and constraints, give whether
        two position relations fit the constraints.
        """
        if player_idx_same is not None:
            if player_idx_same != (
                    self.player_idx == target_position.player_idx):
                return False
        if charactor_idx_same is not None:
            if charactor_idx_same != (
                self.charactor_idx == target_position.charactor_idx
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
        if source_is_active_charactor is not None:
            cidx = match.player_tables[self.player_idx].active_charactor_idx
            return source_is_active_charactor == (self.charactor_idx == cidx)
        if target_is_active_charactor is not None:
            cidx = match.player_tables[
                target_position.player_idx].active_charactor_idx
            return target_is_active_charactor == (
                target_position.charactor_idx == cidx)
        return True


class DamageValue(BaseModel):
    """
    It declares a damage, i.e. damge is received by active/back charactor,
    it will change active charactor with what rule.

    Args:
        position (ObjectPosition): The position of the object who makes the
            damage.
        damage_type (DamageType): The type of the damage, damage, heal, or
            element application (zero damage).
        damage (int): The damage value.
        damage_elemental_type (DamageElementalType): The elemental type of the
            damage.
        charge_cost (int): The charge cost of the damage.
        target_player (Literal['CURRENT', 'ENEMY']): The player who will
            receive the damage.
        target_charactor (Literal['ACTIVE', 'BACK', 'NEXT', 'PREV', 
            'ABSOLUTE']): The charactor who will receive the damage.
            If it is defeated, this damage will be ignored.
        target_charactor_idx (int): The charactor index of the charactor who 
            will receive the damage. Only used when target_charactor is 
            'ABSOLUTE'.
    """

    position: ObjectPosition
    damage_type: DamageType
    damage: int
    damage_elemental_type: DamageElementalType
    charge_cost: int

    # damage which player
    target_player: Literal['CURRENT', 'ENEMY']
    target_charactor: Literal['ACTIVE', 'BACK', 'NEXT', 'PREV', 'ABSOLUTE']
    target_charactor_idx: int = -1


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
    original_value: Any = None

    def is_valid(self, dice_colors: List[DieColor], charge: int, 
                 arcane_legend: bool, strict = True) -> bool:
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

        # then dice check
        assert self.omni_dice_number == 0, 'Omni dice is not supported yet.'
        if self.same_dice_number > 0:
            assert self.elemental_dice_number == 0 and \
                self.any_dice_number == 0, \
                'Same dice and elemental/any dice cannot be both used now.'
        assert not (self.elemental_dice_number > 0 
                    and self.elemental_dice_color is None), \
            'Elemental dice number and color should be both set.'
        if strict:
            if len(dice_colors) != (
                self.elemental_dice_number + self.same_dice_number
                + self.any_dice_number + self.omni_dice_number
            ):
                return False  # dice number not match
        else:
            if len(dice_colors) < (
                self.elemental_dice_number + self.same_dice_number
                + self.any_dice_number + self.omni_dice_number
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
