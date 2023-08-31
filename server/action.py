from enum import Enum
from utils import BaseModel
from typing import Literal, List
from .interaction import (
    ChooseCharactorResponse,
    RerollDiceResponse,
    DeclareRoundEndResponse,
    SwitchCharactorResponse,
)
from .consts import DieColor, ObjectType, SkillType
from .modifiable_values import DamageValue
from .struct import ObjectPosition


class ActionTypes(str, Enum):
    EMPTY = 'EMPTY'
    DRAW_CARD = 'DRAW_CARD'
    RESTORE_CARD = 'RESTORE_CARD'
    REMOVE_CARD = 'REMOVE_CARD'
    CHOOSE_CHARACTOR = 'CHOOSE_CHARACTOR'
    CREATE_DICE = 'CREATE_DICE'
    REMOVE_DICE = 'REMOVE_DICE'
    DECLARE_ROUND_END = 'DECLARE_ROUND_END'
    COMBAT_ACTION = 'COMBAT_ACTION'
    SWITCH_CHARACTOR = 'SWITCH_CHARACTOR'
    CHARGE = 'CHARGE'
    SKILL_END = 'SKILL_END'
    CHARACTOR_DEFEATED = 'CHARACTOR_DEFEATED'
    CREATE_OBJECT = 'CREATE_OBJECT'
    REMOVE_OBJECT = 'REMOVE_OBJECT'
    OBJECT_REMOVED = 'OBJECT_REMOVED'
    CHANGE_OBJECT_USAGE = 'CHANGE_OBJECT_USAGE'
    MOVE_OBJECT = 'MOVE_OBJECT'
    CONSUME_ARCANE_LEGEND = 'CONSUME_ARCANE_LEGEND'

    # system phase actions
    ROUND_PREPARE = 'ROUND_PREPARE'
    ROUND_END = 'ROUND_END'

    # make damage related events
    RECEIVE_DAMAGE = 'RECEIVE_DAMAGE'
    MAKE_DAMAGE = 'MAKE_DAMAGE'
    AFTER_MAKE_DAMAGE = 'AFTER_MAKE_DAMAGE'

    # generate request actions
    GENERATE_CHOOSE_CHARACTOR = 'GENERATE_CHOOSE_CHARACTOR'
    GENERATE_REROLL_DICE = 'GENERATE_REROLL_DICE'


class ActionBase(BaseModel):
    """
    Base class for game actions.
    An action contains arguments to make changes to the game table.

    Attributes:
        action_type (Literal[ActionTypes]): The type of the action.
    """
    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY


class DrawCardAction(ActionBase):
    """
    Action for drawing cards.
    """
    type: Literal[ActionTypes.DRAW_CARD] = ActionTypes.DRAW_CARD
    player_idx: int
    number: int
    blacklist_names: List[str] = []
    whitelist_names: List[str] = []
    blacklist_types: List[ObjectType] = []
    whitelist_types: List[ObjectType] = []
    blacklist_cost_labels: int = 0
    whitelist_cost_labels: int = 0
    draw_if_filtered_not_enough: bool


class RestoreCardAction(ActionBase):
    """
    Action for restoring cards.
    """
    type: Literal[ActionTypes.RESTORE_CARD] = ActionTypes.RESTORE_CARD
    player_idx: int
    card_idxs: List[int]


class RemoveCardAction(ActionBase):
    """
    Action for removing cards.
    """
    type: Literal[ActionTypes.REMOVE_CARD] = ActionTypes.REMOVE_CARD
    position: ObjectPosition
    card_idx: int
    remove_type: Literal['USED', 'BURNED']


class ChooseCharactorAction(ActionBase):
    """
    Action for choosing charactors.
    """
    type: Literal[ActionTypes.CHOOSE_CHARACTOR] = ActionTypes.CHOOSE_CHARACTOR
    player_idx: int
    charactor_idx: int

    @classmethod
    def from_response(cls, response: ChooseCharactorResponse):
        """
        Generate ChooseCharactorAction from ChooseCharactorResponse.
        """
        return cls(
            player_idx = response.player_idx,
            charactor_idx = response.charactor_idx,
        )


class CreateDiceAction(ActionBase):
    """
    Action for creating dice.

    Args:
        player_idx (int): The index of the player to create the dice for.
        number (int): The number of dice to create.
        color (DieColor | None): The color of the dice to create. If None,
            the following generate rules will be activated.
        random (bool): Whether to randomly generate the color of dice.
        different (bool): Whether to generate different colors of dice.
    """
    type: Literal[ActionTypes.CREATE_DICE] = ActionTypes.CREATE_DICE
    player_idx: int
    number: int
    color: DieColor | None = None
    random: bool = False
    different: bool = False


class RemoveDiceAction(ActionBase):
    """
    Action for removing dice.

    Args:
        player_idx (int): The index of the player to remove the dice for.
        dice_idxs (List[int]): The indices of the dice to remove.
    """
    type: Literal[ActionTypes.REMOVE_DICE] = ActionTypes.REMOVE_DICE
    player_idx: int
    dice_idxs: List[int]

    @classmethod
    def from_response(cls, response: RerollDiceResponse):
        """
        Generate RemoveDiceAction from RerollDiceResponse.
        """
        return cls(
            player_idx = response.player_idx,
            dice_idxs = response.reroll_dice_idxs,
        )


class DeclareRoundEndAction(ActionBase):
    """
    Action for declaring the end of the round.
    """
    type: Literal[ActionTypes.DECLARE_ROUND_END] = \
        ActionTypes.DECLARE_ROUND_END
    player_idx: int

    @classmethod
    def from_response(cls, response: DeclareRoundEndResponse):
        """
        Generate DeclareRoundEndAction from DeclareRoundEndResponse.
        """
        return cls(
            player_idx = response.player_idx,
        )


class CombatActionAction(ActionBase):
    """
    Do a combat action, i.e. skill, switch, end.
    the position means the action source, i.e. the charactor who use the skill,
    or the charactor who switch out.
    """
    type: Literal[ActionTypes.COMBAT_ACTION] = ActionTypes.COMBAT_ACTION
    action_type: Literal['SKILL', 'SWITCH', 'END']
    position: ObjectPosition


class SwitchCharactorAction(ActionBase):
    """
    Action for switching charactor.
    """
    type: Literal[ActionTypes.SWITCH_CHARACTOR] = ActionTypes.SWITCH_CHARACTOR
    player_idx: int
    charactor_idx: int

    @classmethod
    def from_response(cls, response: SwitchCharactorResponse):
        """
        Generate SwitchCharactorAction from SwitchCharactorResponse.
        """
        return cls(
            player_idx = response.player_idx,
            charactor_idx = response.charactor_idx,
        )


class MakeDamageAction(ActionBase):
    """
    Action for making damage. Heal treats as negative damage. Elemental 
    applies to the charactor (e.g. Kokomi) treats as zero damage.

    Args:
        player_idx (int): The index of the player to make damage from.
        damage_value_list (List[DamageValue]): The damage values to make.
        target_idx (int): The index of the player to make damage to.
        charactor_change_rule (Literal['NONE', 'NEXT', 'PREV', 'ABSOLUTE']):
            The rule of charactor change. 
        charactor_change_idx (int): The charactor index of the charactor who 
            will be changed to. Only used when charactor_change_rule is 
            'ABSOLUTE'. If it is defeated, select by default order. (e.g.
            absolute choose charactor 2, but it is defeated, then choose
            0, 1, ...)
    """
    type: Literal[ActionTypes.MAKE_DAMAGE] = ActionTypes.MAKE_DAMAGE
    player_idx: int
    damage_value_list: List[DamageValue]
    target_idx: int

    # charactor change
    charactor_change_rule: Literal['NONE', 'NEXT', 'PREV', 'ABSOLUTE'] = 'NONE'
    charactor_change_idx: int = -1


class ChargeAction(ActionBase):
    """
    Action for charging.
    """
    type: Literal[ActionTypes.CHARGE] = ActionTypes.CHARGE
    player_idx: int
    charactor_idx: int
    charge: int


class SkillEndAction(ActionBase):
    """
    Action for ending skill.
    """
    type: Literal[ActionTypes.SKILL_END] = ActionTypes.SKILL_END
    position: ObjectPosition
    skill_type: SkillType


class CharactorDefeatedAction(ActionBase):
    """
    Action for charactor defeated.
    """
    type: Literal[ActionTypes.CHARACTOR_DEFEATED] = \
        ActionTypes.CHARACTOR_DEFEATED
    player_idx: int
    charactor_idx: int


class CreateObjectAction(ActionBase):
    """
    Action for creating objects, e.g. status, summons, supports.
    Note some objects are not created but moved, e.g. equipments and supports,
    for these objects, do not use this action.
    """
    type: Literal[ActionTypes.CREATE_OBJECT] = \
        ActionTypes.CREATE_OBJECT
    object_position: ObjectPosition
    object_name: str
    object_arguments: dict


class RemoveObjectAction(ActionBase):
    """
    Action for removing objects. 

    Args:
        object_position (ObjectPosition): The ID and position of the 
            object to remove.
    """
    type: Literal[ActionTypes.REMOVE_OBJECT] = \
        ActionTypes.REMOVE_OBJECT
    object_position: ObjectPosition


class ChangeObjectUsageAction(ActionBase):
    """
    Action for changing object usage.
    """
    type: Literal[ActionTypes.CHANGE_OBJECT_USAGE] = \
        ActionTypes.CHANGE_OBJECT_USAGE
    object_position: ObjectPosition
    change_type: Literal['DELTA', 'SET']
    change_usage: int
    min_usage: int = 0
    max_usage: int = 999


class MoveObjectAction(ActionBase):
    """
    Action for moving objects.
    """
    type: Literal[ActionTypes.MOVE_OBJECT] = \
        ActionTypes.MOVE_OBJECT
    object_position: ObjectPosition
    target_position: ObjectPosition


class ConsumeArcaneLegendAction(ActionBase):
    """
    Action for consuming arcane legend.
    """
    type: Literal[ActionTypes.CONSUME_ARCANE_LEGEND] = \
        ActionTypes.CONSUME_ARCANE_LEGEND
    player_idx: int


class GenerateChooseCharactorRequestAction(ActionBase):
    """
    Action for generating choose charactor action.
    """
    type: Literal[ActionTypes.GENERATE_CHOOSE_CHARACTOR] = \
        ActionTypes.GENERATE_CHOOSE_CHARACTOR
    player_idx: int


class GenerateRerollDiceRequestAction(ActionBase):
    """
    Action for generating reroll dice request.
    """
    type: Literal[ActionTypes.GENERATE_REROLL_DICE] = \
        ActionTypes.GENERATE_REROLL_DICE
    player_idx: int
    reroll_times: int


Actions = (
    ActionBase | DrawCardAction | RestoreCardAction | RemoveCardAction 
    | ChooseCharactorAction | CreateDiceAction | RemoveDiceAction
    | DeclareRoundEndAction | CombatActionAction | SwitchCharactorAction
    | MakeDamageAction | ChargeAction | SkillEndAction 
    | CharactorDefeatedAction | GenerateChooseCharactorRequestAction
    | CreateObjectAction | RemoveObjectAction | ChangeObjectUsageAction
    | MoveObjectAction | ConsumeArcaneLegendAction
)
