from enum import Enum
from ..utils import BaseModel
from typing import Literal, List, Tuple
from .interaction import (
    ChooseCharacterResponse,
    RerollDiceResponse,
    DeclareRoundEndResponse,
    SwitchCharacterResponse,
)
from .consts import DieColor, ObjectType, SkillType
from .modifiable_values import DamageValue
from .struct import MultipleObjectPosition, ObjectPosition


class ActionTypes(str, Enum):
    EMPTY = "EMPTY"
    DRAW_CARD = "DRAW_CARD"
    RESTORE_CARD = "RESTORE_CARD"
    REMOVE_CARD = "REMOVE_CARD"
    CHOOSE_CHARACTER = "CHOOSE_CHARACTER"
    CREATE_DICE = "CREATE_DICE"
    REMOVE_DICE = "REMOVE_DICE"
    DECLARE_ROUND_END = "DECLARE_ROUND_END"
    ACTION_END = "ACTION_END"
    SWITCH_CHARACTER = "SWITCH_CHARACTER"
    CHARGE = "CHARGE"
    USE_SKILL = "USE_SKILL"
    USE_CARD = "USE_CARD"
    SKILL_END = "SKILL_END"
    CHARACTER_DEFEATED = "CHARACTER_DEFEATED"
    CHARACTER_REVIVE = "CHARACTER_REVIVE"
    CREATE_OBJECT = "CREATE_OBJECT"
    CREATE_RANDOM_OBJECT = "CREATE_RANDOM_OBJECT"
    REMOVE_OBJECT = "REMOVE_OBJECT"
    OBJECT_REMOVED = "OBJECT_REMOVED"
    CHANGE_OBJECT_USAGE = "CHANGE_OBJECT_USAGE"
    MOVE_OBJECT = "MOVE_OBJECT"
    CONSUME_ARCANE_LEGEND = "CONSUME_ARCANE_LEGEND"

    # system phase events
    GAME_START = "GAME_START"
    ROUND_PREPARE = "ROUND_PREPARE"
    PLAYER_ACTION_START = "PLAYER_ACTION_START"
    ROUND_END = "ROUND_END"

    # make damage related events
    RECEIVE_DAMAGE = "RECEIVE_DAMAGE"
    MAKE_DAMAGE = "MAKE_DAMAGE"
    AFTER_MAKE_DAMAGE = "AFTER_MAKE_DAMAGE"

    # generate request actions
    GENERATE_CHOOSE_CHARACTER = "GENERATE_CHOOSE_CHARACTER"
    GENERATE_REROLL_DICE = "GENERATE_REROLL_DICE"
    GENERATE_SWITCH_CARD = "GENERATE_SWITCH_CARD"

    # change game state actions
    SKIP_PLAYER_ACTION = "SKIP_PLAYER_ACTION"


class ActionBase(BaseModel):
    """
    Base class for game actions.
    An action contains arguments to make changes to the game table.

    Attributes:
        action_type (Literal[ActionTypes]): The type of the action.
        record_level (int): The level of the action to record in match.history,
            lower level means more important. It should be a positive number.
    """

    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY

    record_level: int = 100


class DrawCardAction(ActionBase):
    """
    Action for drawing cards.
    """

    type: Literal[ActionTypes.DRAW_CARD] = ActionTypes.DRAW_CARD
    record_level: int = 10
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
    record_level: int = 20
    position: ObjectPosition
    remove_type: Literal["USED", "BURNED"]


class ChooseCharacterAction(ActionBase):
    """
    Action for choosing characters.
    """

    type: Literal[ActionTypes.CHOOSE_CHARACTER] = ActionTypes.CHOOSE_CHARACTER
    record_level: int = 10
    player_idx: int
    character_idx: int

    @classmethod
    def from_response(cls, response: ChooseCharacterResponse):
        """
        Generate ChooseCharacterAction from ChooseCharacterResponse.
        """
        return cls(
            player_idx=response.player_idx,
            character_idx=response.character_idx,
        )


# 5


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
            if you want to generate random but never OMNI die, generate one
            different die. If multiple, use multiple action.
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
            player_idx=response.player_idx,
            dice_idxs=response.reroll_dice_idxs,
        )


class DeclareRoundEndAction(ActionBase):
    """
    Action for declaring the end of the round.
    """

    type: Literal[ActionTypes.DECLARE_ROUND_END] = ActionTypes.DECLARE_ROUND_END
    record_level: int = 10
    player_idx: int

    @classmethod
    def from_response(cls, response: DeclareRoundEndResponse):
        """
        Generate DeclareRoundEndAction from DeclareRoundEndResponse.
        """
        return cls(
            player_idx=response.player_idx,
        )


class ActionEndAction(ActionBase):
    """
    Action end, and if is a combat action, change current player.
    the position means the action source, i.e. the skill,
    or the character who switch out.
    """

    type: Literal[ActionTypes.ACTION_END] = ActionTypes.ACTION_END
    action_label: int  # Refer to PlayerActionLabels
    do_combat_action: bool
    position: ObjectPosition


class SwitchCharacterAction(ActionBase):
    """
    Action for switching character.
    """

    type: Literal[ActionTypes.SWITCH_CHARACTER] = ActionTypes.SWITCH_CHARACTER
    record_level: int = 10
    player_idx: int
    character_idx: int

    @classmethod
    def from_response(cls, response: SwitchCharacterResponse):
        """
        Generate SwitchCharacterAction from SwitchCharacterResponse.
        """
        return cls(
            player_idx=response.player_idx,
            character_idx=response.request.target_character_idx,
        )


# 10


class ChargeAction(ActionBase):
    """
    Action for charging.
    """

    type: Literal[ActionTypes.CHARGE] = ActionTypes.CHARGE
    player_idx: int
    character_idx: int
    charge: int


class UseSkillAction(ActionBase):
    """
    Action for using skill.
    """

    type: Literal[ActionTypes.USE_SKILL] = ActionTypes.USE_SKILL
    record_level: int = 10
    skill_position: ObjectPosition


class UseCardAction(ActionBase):
    """
    Action for using card.
    """

    type: Literal[ActionTypes.USE_CARD] = ActionTypes.USE_CARD
    record_level: int = 10
    card_position: ObjectPosition
    target: ObjectPosition | MultipleObjectPosition | None


class SkillEndAction(ActionBase):
    """
    Action for ending skill.
    """

    type: Literal[ActionTypes.SKILL_END] = ActionTypes.SKILL_END
    position: ObjectPosition
    target_position: ObjectPosition  # always poopnent initial active character now  # noqa: E501
    skill_type: SkillType


class CharacterDefeatedAction(ActionBase):
    """
    Action for character defeated.
    """

    type: Literal[ActionTypes.CHARACTER_DEFEATED] = ActionTypes.CHARACTER_DEFEATED
    player_idx: int
    character_idx: int


# 15


class CreateObjectAction(ActionBase):
    """
    Action for creating objects, e.g. status, summons, supports.
    Note some objects are not created but moved, e.g. equipment and supports,
    for these objects, do not use this action.
    """

    type: Literal[ActionTypes.CREATE_OBJECT] = ActionTypes.CREATE_OBJECT
    object_position: ObjectPosition
    object_name: str
    object_arguments: dict


class CreateRandomObjectAction(ActionBase):
    """
    Action for creating random objects. A list of names are provided, and
    `number` of them will be created by uniformly selecting from the list and doing
    `CreateObjectAction` for each of them.
    NOTE: some actions will not generate existing objects, e.g. elemental skill of
    Rhodeia will not summoning existing objects unless full. This action will not deal
    with such situation, you need to write logic to filter out existing objects before
    creating this action.
    """

    type: Literal[ActionTypes.CREATE_OBJECT] = ActionTypes.CREATE_OBJECT
    object_position: ObjectPosition
    object_names: List[str]
    object_arguments: dict
    number: int

    def select_by_idx(
        self, idx: int
    ) -> Tuple[CreateObjectAction, "CreateRandomObjectAction"]:
        """
        Select an object name by index and create a `CreateObjectAction` for it.
        It will also return a new `CreateRandomObjectAction` with the same
        arguments but with the `number` reduced by 1 and the selected object
        name removed from the list.

        Returns:
            CreateObjectAction: The action for creating the object.
            CreateRandomObjectAction: The new action with the `number` reduced
                by 1 and the selected object name removed from the list.
        """
        selected = self.object_names[idx]
        others = self.object_names[:idx] + self.object_names[idx + 1 :]
        return (
            CreateObjectAction(
                object_position=self.object_position,
                object_name=selected,
                object_arguments=self.object_arguments,
            ),
            CreateRandomObjectAction(
                object_position=self.object_position,
                object_names=others,
                object_arguments=self.object_arguments,
                number=self.number - 1,
            ),
        )


class RemoveObjectAction(ActionBase):
    """
    Action for removing objects.

    Args:
        object_position (ObjectPosition): The ID and position of the
            object to remove.
    """

    type: Literal[ActionTypes.REMOVE_OBJECT] = ActionTypes.REMOVE_OBJECT
    object_position: ObjectPosition


class ChangeObjectUsageAction(ActionBase):
    """
    Action for changing object usage. change in delta.
    """

    type: Literal[ActionTypes.CHANGE_OBJECT_USAGE] = ActionTypes.CHANGE_OBJECT_USAGE
    object_position: ObjectPosition
    change_usage: int
    min_usage: int = 0
    max_usage: int = 999


class MoveObjectAction(ActionBase):
    """
    Action for moving objects.
    """

    type: Literal[ActionTypes.MOVE_OBJECT] = ActionTypes.MOVE_OBJECT
    record_level: int = 10
    object_position: ObjectPosition
    target_position: ObjectPosition
    # for Master of Weaponry etc. in 4.1, when mark true, reset round usage
    reset_usage: bool = False


# 20


class MakeDamageAction(ActionBase):
    """
    Action for making damage. Heal treats as negative damage. Elemental
    applies to the character (e.g. Kokomi) treats as zero damage.

    Args:
        damage_value_list (List[DamageValue]): The damage values to make.
        do_character_change (bool): Whether to change character after making
            damage.
    """

    type: Literal[ActionTypes.MAKE_DAMAGE] = ActionTypes.MAKE_DAMAGE
    record_level: int = 10
    damage_value_list: List[DamageValue]

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        for damage_value in self.damage_value_list:
            assert (
                damage_value.position.id == self.damage_value_list[0].position.id
            ), "all damage should from same source"


class ConsumeArcaneLegendAction(ActionBase):
    """
    Action for consuming arcane legend.
    """

    type: Literal[ActionTypes.CONSUME_ARCANE_LEGEND] = ActionTypes.CONSUME_ARCANE_LEGEND
    player_idx: int


class GenerateChooseCharacterRequestAction(ActionBase):
    """
    Action for generating choose character action.
    """

    type: Literal[
        ActionTypes.GENERATE_CHOOSE_CHARACTER
    ] = ActionTypes.GENERATE_CHOOSE_CHARACTER
    player_idx: int


class GenerateRerollDiceRequestAction(ActionBase):
    """
    Action for generating reroll dice request.
    """

    type: Literal[ActionTypes.GENERATE_REROLL_DICE] = ActionTypes.GENERATE_REROLL_DICE
    player_idx: int
    reroll_times: int


class SkipPlayerActionAction(ActionBase):
    """
    Action for skipping current player action. As skipping will cause action end, its
    variables are the same as ActionEndAction.
    """

    type: Literal[ActionTypes.SKIP_PLAYER_ACTION] = ActionTypes.SKIP_PLAYER_ACTION
    action_label: int  # Refer to PlayerActionLabels
    do_combat_action: bool
    position: ObjectPosition

    def get_action_end_action(self):
        return ActionEndAction(
            action_label=self.action_label,
            do_combat_action=self.do_combat_action,
            position=self.position,
        )


# 25


class CharacterReviveAction(ActionBase):
    """
    Action for character revive.
    """

    type: Literal[ActionTypes.CHARACTER_REVIVE] = ActionTypes.CHARACTER_REVIVE
    record_level: int = 10
    player_idx: int
    character_idx: int
    revive_hp: int


class GenerateSwitchCardRequestAction(ActionBase):
    """
    Action for generating switch card request.
    """

    type: Literal[ActionTypes.GENERATE_SWITCH_CARD] = ActionTypes.GENERATE_SWITCH_CARD
    player_idx: int


Actions = (
    ActionBase
    | DrawCardAction
    | RestoreCardAction
    | RemoveCardAction
    | ChooseCharacterAction
    # 5
    | CreateDiceAction
    | RemoveDiceAction
    | DeclareRoundEndAction
    | ActionEndAction
    | SwitchCharacterAction
    # 10
    | ChargeAction
    | UseSkillAction
    | UseCardAction
    | SkillEndAction
    | CharacterDefeatedAction
    # 15
    | CreateObjectAction
    | CreateRandomObjectAction
    | RemoveObjectAction
    | ChangeObjectUsageAction
    | MoveObjectAction
    # 20
    | MakeDamageAction
    | ConsumeArcaneLegendAction
    | GenerateChooseCharacterRequestAction
    | GenerateRerollDiceRequestAction
    | SkipPlayerActionAction
    # 25
    | CharacterReviveAction
    | GenerateSwitchCardRequestAction
)
