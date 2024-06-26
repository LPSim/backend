import os
import logging
import copy
import random
from typing import Literal, List, Any, Dict, Tuple
from enum import Enum
from pydantic import PrivateAttr, validator
import dictdiffer

from .event_controller import EventController
from .summon.base import SummonBase
from .status.team_status.base import TeamStatusBase
from .status.character_status.base import CharacterStatusBase
from ..utils import BaseModel, get_instance
from .deck import Deck
from .player_table import PlayerTable
from .action import (
    ActionBase,
    ActionTypes,
    Actions,
    DrawCardAction,
    RestoreCardAction,
    RemoveCardAction,
    ChooseCharacterAction,
    CreateDiceAction,
    RemoveDiceAction,
    DeclareRoundEndAction,
    ActionEndAction,
    SkipPlayerActionAction,
    SwitchCharacterAction,
    MakeDamageAction,
    ChargeAction,
    UseCardAction,
    UseSkillAction,
    SkillEndAction,
    CreateObjectAction,
    CreateRandomObjectAction,
    RemoveObjectAction,
    ChangeObjectUsageAction,
    MoveObjectAction,
    CharacterDefeatedAction,
    GenerateChooseCharacterRequestAction,
    GenerateRerollDiceRequestAction,
    CharacterReviveAction,
    ConsumeArcaneLegendAction,
    GenerateSwitchCardRequestAction,
    SwitchCardAction,
)
from .interaction import (
    Requests,
    Responses,
    SwitchCardRequest,
    SwitchCardResponse,
    ChooseCharacterRequest,
    ChooseCharacterResponse,
    RerollDiceRequest,
    RerollDiceResponse,
    SwitchCharacterRequest,
    SwitchCharacterResponse,
    ElementalTuningRequest,
    ElementalTuningResponse,
    DeclareRoundEndRequest,
    DeclareRoundEndResponse,
    UseSkillRequest,
    UseSkillResponse,
    UseCardRequest,
    UseCardResponse,
)
from .consts import (
    CostLabels,
    DamageElementalType,
    DamageType,
    DieColor,
    ELEMENT_TO_DIE_COLOR,
    DAMAGE_TYPE_TO_ELEMENT,
    ElementalReactionType,
    ObjectPositionType,
    ObjectType,
    PlayerActionLabels,
    SkillType,
)
from .event import (
    CharacterReviveEventArguments,
    PlayerActionStartEventArguments,
    ConsumeArcaneLegendEventArguments,
    EventArguments,
    EventArgumentsBase,
    DrawCardEventArguments,
    GameStartEventArguments,
    RestoreCardEventArguments,
    RemoveCardEventArguments,
    ChooseCharacterEventArguments,
    CreateDiceEventArguments,
    RemoveDiceEventArguments,
    RoundPrepareEventArguments,
    DeclareRoundEndEventArguments,
    ActionEndEventArguments,
    SwitchCharacterEventArguments,
    ChargeEventArguments,
    SkillEndEventArguments,
    ReceiveDamageEventArguments,
    MakeDamageEventArguments,
    AfterMakeDamageEventArguments,
    CharacterDefeatedEventArguments,
    RoundEndEventArguments,
    CreateObjectEventArguments,
    RemoveObjectEventArguments,
    ChangeObjectUsageEventArguments,
    MoveObjectEventArguments,
    UseCardEventArguments,
    UseSkillEventArguments,
    SwitchCardEventArguments,
)
from .object_base import CardBase, ObjectBase
from .modifiable_values import (
    CombatActionValue,
    FullCostValue,
    ModifiableValueBase,
    InitialDiceColorValue,
    ModifiableValueTypes,
    RerollValue,
    CostValue,
    DamageMultiplyValue,
    DamageDecreaseValue,
    UseCardValue,
)
from .struct import ObjectPosition, Cost
from .elemental_reaction import (
    check_elemental_reaction,
    apply_elemental_reaction,
)
from .event_handler import SystemEventHandlerBase, SystemEventHandler


try:
    import numpy as np
except ImportError:  # pragma: no cover
    # in legacy version, we use numpy as random generator. And in newer version, we
    # use random as random generator. If numpy is not installed, we cannot set random
    # state with numpy version states.
    pass


class MatchState(str, Enum):
    """
    Enum representing the state of a match.

    Attributes:
        INVALID (str): The match is invalid. Should not fall into it in common
            situations.
        ERROR (str): The match has encountered an error. Should not fall into
            it in common situations.
        WAITING (str): The match is waiting for start.
        STARTING (str): The match is starting, will generate initial objects,
            decide who is the first player, draw initial card, etc.
        STARTING_CARD_SWITCH (str): Waiting for players to switch cards.
        STARTING_CHOOSE_CHARACTER (str): Waiting for players to choose
            characters.
        GAME_START: The game has started, trigger some passive skills.
        ROUND_START (str): A new round is starting.
        ROUND_ROLL_DICE (str): Waiting for players to re-roll dice.
        ROUND_PREPARING (str): Preparing phase starts.
        PLAYER_ACTION_START (str): Player action phase start.
        PLAYER_ACTION_REQUEST (str): Waiting for response from player, and
            after player has decided its action, the action is being executed.
            Execution may be interrupted by requests, e.g. someone is knocked
            out, need to re-roll dice. When all requests and actions are clear,
            change to ROUND_ENDING.
        ROUND_ENDING (str): Ending phase starts.
        ROUND_ENDED (str): The round has ended.
        ENDED (str): The match has ended.
    """

    INVALID = "INVALID"
    ERROR = "ERROR"
    WAITING = "WAITING"

    STARTING = "STARTING"
    STARTING_CARD_SWITCH = "STARTING_CARD_SWITCH"
    STARTING_CHOOSE_CHARACTER = "STARTING_CHOOSE_CHARACTER"

    GAME_START = "GAME_START"

    ROUND_START = "ROUND_START"
    ROUND_ROLL_DICE = "ROUND_ROLL_DICE"
    ROUND_PREPARING = "ROUND_PREPARING"

    PLAYER_ACTION_START = "PLAYER_ACTION_START"
    PLAYER_ACTION_REQUEST = "PLAYER_ACTION_REQUEST"

    ROUND_ENDING = "ROUND_ENDING"
    ROUND_ENDED = "ROUND_ENDED"

    ENDED = "ENDED"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class MatchConfig(BaseModel):
    """
    Basic configs for the match.
    """

    random_first_player: bool = True
    player_go_first: Literal[0, 1] = 0
    check_deck_restriction: bool = True
    initial_hand_size: int = 5
    initial_card_draw: int = 2
    initial_dice_number: int = 8
    initial_dice_reroll_times: int = 1
    card_number: int | None = 30
    max_same_card_number: int | None = 2
    character_number: int | None = 3
    max_round_number: int = 15
    max_hand_size: int = 10
    max_dice_number: int = 16
    max_summon_number: int = 4
    max_support_number: int = 4

    """
    When set True, if it is player turn, the predictions of using skills will
    be generated. The predictions will be stored in Match.skill_predictions.
    NOTE: It is slow to generate predictions, normally should not use it in
    non-frontend tasks.
    """
    make_skill_prediction: bool = False

    """
    When history level is greater than 0, histories will be recorded when 
    certain action is done or need response from player. For requests, 
    histories will be recorded after the request is generated, and history
    level is positive; for actions, histories will be recorded after the 
    action is done, and the record_level of the action is lower or equal to
    history level. 
    By default, history is compressed, which means that only the difference
    between two consecutive histories, and the first and last history, is
    recorded. If compress_history is set to False, all histories will be
    recorded. When compressed, it will consume less memory, but it will take
    more time in calling Match.new_match_from_history.

    NOTE: It is slow to save history, normally should not use it in
    non-frontend tasks.
    """
    history_level: int = 0
    compress_history: bool = True

    """
    config that used to re-create the match easier. when replay mode is 
    activated, randomness will be disabled. If self._random or 
    self._random_shuffle is called, it will raise error.
    For dice colors, all generated color will be omni and omni dice is able 
    to be tuned.
    For cards, card shuffle will be disabled. Drawing card with card 
    filters, e.g. NRE, will only draw top card, and if top card is not target,
    it stops drawing. Drawing card with replacement will put the replaced
    card into the bottom of table deck.
    For random effects, e.g. Abyss Sommon, or Rhodeia's skill, CreateRandomObjectAction
    will read orders from random_object_information. When action is called, it will
    check whether first name is in object names, create that object and remove the name.

    TODO: As all dice are omni, Liben and Vanarana may have non-reproducible
    results. Need to fix it.
    """
    recreate_mode: bool = False
    random_object_information: List[str] = []

    def check_config(self) -> bool:
        """
        Check whether the config is legal.
        """
        if (
            self.initial_hand_size < 0
            or self.initial_card_draw < 0
            or self.initial_dice_number < 0
            or self.initial_dice_reroll_times < 0
            or (self.card_number is not None and self.card_number < 0)
            or (self.max_same_card_number is not None and self.max_same_card_number < 0)
            or (self.character_number is not None and self.character_number < 0)
            or self.max_round_number <= 0
            or self.max_hand_size < 0
            or self.max_dice_number < 0
            or self.max_summon_number < 0
            or self.max_support_number < 0
        ):
            return False
        if self.initial_hand_size > self.max_hand_size:
            logging.error(
                "initial hand size should not be greater than " "max hand size"
            )
            return False
        if self.initial_card_draw > self.max_hand_size:
            logging.error(
                "initial card draw should not be greater than " "max hand size"
            )
            return False

        if self.card_number is not None and self.initial_card_draw > self.card_number:
            logging.error("initial card draw should not be greater than " "card number")
            return False
        if self.initial_dice_number > self.max_dice_number:
            logging.error(
                "initial dice number should not be greater than " "max dice number"
            )
            return False
        if self.history_level < 0:
            logging.error("history level should not be less than 0")
            return False
        return True


class Match(BaseModel):
    """ """

    name: Literal["Match"] = "Match"

    # TODO what is the difference between different version?
    # 0.0.5: officially accounced the deck order, and change relative actions.
    version: Literal["0.0.1", "0.0.2", "0.0.3", "0.0.4", "0.0.5"] = "0.0.5"

    config: MatchConfig = MatchConfig()

    """
    history logger and last action recorder. 
    history_diff[i] records the difference between _history[i - 1] and 
    _history[i], which is used in data transmission.
    action_info is used to record information that generated during the action,
    e.g. for MakeDamageAction, it will record the detailed damage information, 
    which has applied elemental reaction and value modification.
    """
    _history: List["Match"] = PrivateAttr(default_factory=list)
    _history_diff: List = PrivateAttr(default_factory=list)
    last_action: Actions = ActionBase()
    action_info: Any = {}

    # skill prediction results. It will generate in player action request.
    # check _predict_skill for detailed logics.
    # if _skill_prediction_mode is True, it will have different behavior in
    # some functions.
    _prediction_mode: bool = PrivateAttr(False)
    skill_predictions: List[Any] = []

    # random state
    random_state: List[Any] = []
    _random_state: Any = PrivateAttr(None)

    # event handlers to implement special rules.
    event_handlers: List[SystemEventHandlerBase] = [
        SystemEventHandler(),
        # OmnipotentGuideEventHandler(),
    ]

    # match information
    round_number: int = 0
    current_player: int = -1
    player_tables: List[PlayerTable] = []
    state: MatchState = MatchState.WAITING
    event_controller = EventController()
    requests: List[Requests] = []
    winner: int = -1

    # debug params
    _debug_save_appeared_object_names: bool = PrivateAttr(False)
    _debug_appeared_object_names_versions: Any = PrivateAttr({})
    _debug_save_file_name: str = PrivateAttr("")

    # In event chain, all removed objects will firstly move to the trashbin.
    # If some object explicitly claims that some event handlers will work in
    # trashbin, these events will be triggered in trashbin. After all event
    # chain cleared, all objects in trashbin will be removed.
    trashbin: List[CharacterStatusBase | TeamStatusBase | CardBase | SummonBase] = []

    @validator("event_handlers", each_item=True, pre=True)
    def parse_event_handlers(cls, v):
        return get_instance(SystemEventHandlerBase, v)

    # @validator('requests', each_item = True, pre = True)
    # def parse_requests(cls, v):
    #     return get_instance(Requests, v)

    @validator("trashbin", each_item=True, pre=True)
    def parse_trashbin(cls, v):
        return get_instance(
            CharacterStatusBase | TeamStatusBase | CardBase | SummonBase, v
        )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if len(self.player_tables) == 0:
            self.player_tables.append(
                PlayerTable(
                    version=self.version,
                    player_idx=0,
                )
            )
            self.player_tables.append(
                PlayerTable(
                    version=self.version,
                    player_idx=1,
                )
            )
        self._init_random_state()

        debug_level = os.getenv("LPSIM_DEBUG_LEVEL", None)
        if debug_level is not None:  # pragma: no cover
            logging.getLogger().setLevel(debug_level)

    def new_match_from_history(self, history_idx: int) -> "Match":
        """
        return a new match from history of current match. Histories after
        history_idx will be removed, and histories before history_idx is still
        valid.
        """
        history = self._history[:]
        history_diff = self._history_diff[:]
        if len(history_diff) <= history_idx or history_idx < 0:
            raise AssertionError("State not found")
        if self.config.compress_history:
            # calculate the target history
            target_history_dict = history[0].dict()
            for diff in history_diff[1 : history_idx + 1]:
                diff = copy.deepcopy(diff)
                dictdiffer.patch(diff, target_history_dict, in_place=True)
            target_history = Match(**target_history_dict)
            match = target_history.copy(deep=True)
            match._history = [history[0]]
            if history_idx > 0:
                match._history.append(target_history)
            match._history_diff = history_diff[: history_idx + 1]
        else:
            target_history = history[history_idx]
            match = target_history.copy(deep=True)
            match._history = history[: history_idx + 1]
            match._history_diff = history_diff[: history_idx + 1]
        return match

    def copy(self, *argv, **kwargs) -> "Match":
        """
        Copy the match, and init random state of new match.
        """
        ret = super().copy(*argv, **kwargs)
        ret._init_random_state()
        return ret

    def _init_random_state(self):
        if self.config.recreate_mode:
            # no need to init random state
            return
        if self.random_state:
            if self.random_state[0] == "MT19937":
                assert "np" in globals(), (
                    "numpy is not installed, cannot set random state with numpy "
                    "version states."
                )
                random_state = self.random_state[:]
                random_state[1] = np.array(random_state[1], dtype="uint32")
                self._random_state = np.random.RandomState()
                self._random_state.set_state(random_state)
            else:
                random_state = (
                    self.random_state[0],
                    tuple(self.random_state[1]),
                    self.random_state[2],
                )
                self._random_state = random.Random()
                self._random_state.setstate(random_state)
        else:
            # random state not set, create new random state
            self._random_state = random.Random()
            self._save_random_state()

    def _save_history(self) -> None:
        """
        Save the current match to history.
        """
        if self._prediction_mode:
            # do not save history in prediction mode
            return
        hist = self._history[:]
        hist_diff = self._history_diff[:]
        self._history.clear()
        self._history_diff.clear()
        copy = self.copy(deep=True)
        self._history += hist
        self._history_diff += hist_diff
        self._history.append(copy)
        if len(self._history) == 1:
            self._history_diff.append(None)
        else:
            self._history_diff.append(
                list(
                    dictdiffer.diff(self._history[-2].dict(), self._history[-1].dict())
                )
            )
            # remove prev values of 'remove' in diff
            diff = self._history_diff[-1]
            for d in diff:
                if d[0] == "remove":
                    for i in range(len(d[2])):
                        d[2][i] = (d[2][i][0], None)
            if len(diff) == 0:
                # no different, drop the last history
                self._history.pop()
                self._history_diff.pop()
        if self.config.compress_history:
            # If compress history, only save the first and last history.
            # When self._history length larger than 2, only keep the first and
            # last history.
            if len(self._history) > 2:
                self._history = [self._history[0], self._history[-1]]

    def record_last_action_history(self):
        """
        Record history based on last action.
        When history level is 0, no information will be recorded.
        With higher history level, more information will be recorded.
        By default, all actions have history level 100.
        """
        if (
            self.config.history_level >= self.last_action.record_level
            and self.last_action.type != ActionTypes.EMPTY
        ):  # pragma: no cover
            self._save_history()
        # after potential history recording, reset last action
        self.last_action = ActionBase()

    def _debug_save_appeared_object_names_to_file(self):  # pragma: no cover
        # save appeared object names and descs
        if self._debug_save_file_name == "":
            import time

            self._debug_save_file_name = str(time.time())
        for obj in self.get_object_list():
            name = obj.name  # type: ignore
            type = obj.type
            version = ""
            if hasattr(obj, "version"):
                version = obj.version  # type: ignore
            desc = ""
            if hasattr(obj, "desc"):
                desc = obj.desc  # type: ignore
            if type == ObjectType.SKILL:
                # record skill type and its corresponding character and
                # character's version
                character = self.player_tables[obj.position.player_idx].characters[
                    obj.position.character_idx
                ]
                skill_type = obj.skill_type  # type: ignore
                type = f"{type}_{character.name}_{skill_type}"
                version = character.version
            elif type == ObjectType.TALENT:
                # record its corresponding character
                type = f"{type}_{obj.character_name}"  # type: ignore
            if type not in self._debug_appeared_object_names_versions:
                self._debug_appeared_object_names_versions[type] = {}
            if name not in self._debug_appeared_object_names_versions[type]:
                self._debug_appeared_object_names_versions[type][name] = {}
            self._debug_appeared_object_names_versions[type][name][version] = desc
        import json

        target_folder = "logs/obj_name_descs"
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        open(f"{target_folder}/{self._debug_save_file_name}.txt", "w").write(
            json.dumps(self._debug_appeared_object_names_versions, indent=2)
        )

    def set_deck(self, decks: List[Deck]):
        """
        Set the deck of the match.
        """
        if self.state != MatchState.WAITING:
            raise ValueError("Match is not in waiting state.")
        assert len(decks) == len(self.player_tables)
        for player_table, deck in zip(self.player_tables, decks):
            player_table.player_deck_information = deck

    def get_history_json(
        self, filename: str | None = None
    ) -> List[str]:  # pragma: no cover
        """
        Return the history of the match in jsonl format.
        if filename is set, save the history to file.
        """
        assert (
            not self.config.compress_history
        ), "History is compressed, cannot get history json."
        res = [match.json() for match in self._history]
        if filename is not None:
            with open(filename, "w") as f:
                f.write("\n".join(res))
        return res

    def need_respond(self, player_idx: int) -> bool:
        """
        Check if the player needs to respond to any request.
        """
        for request in self.requests:
            if request.player_idx == player_idx:
                return True
        return False

    def _save_random_state(self):
        """
        Save the random state.
        """
        if isinstance(self._random_state, random.Random):
            self.random_state = list(self._random_state.getstate())
            self.random_state[1] = list(self.random_state[1])
            return
        elif isinstance(self._random_state, np.random.RandomState):
            self.random_state = list(self._random_state.get_state(legacy=True))
            self.random_state[1] = self.random_state[1].tolist()
        else:
            raise AssertionError(
                f"Random state type {type(self._random_state)} not recognized."
            )

    def _random(self):
        """
        Return a random number ranges 0-1 based on random_state, and save new
        random state.
        """
        assert (
            not self.config.recreate_mode
        ), "In recreate mode, random functions should not be called."
        ret = self._random_state.random()
        self._save_random_state()
        return ret

    def _random_shuffle(self, array: List):
        """
        Shuffle the array based on random_state.
        """
        assert (
            not self.config.recreate_mode
        ), "In recreate mode, random functions should not be called."
        self._random_state.shuffle(array)
        self._save_random_state()

    def _set_match_state(self, new_state: MatchState):
        logging.info(f"Match state change from {self.state} to " f"{new_state}.")
        self.state = new_state

    def start(self) -> Tuple[bool, Any]:
        """
        Start a new match. MatchState should be WAITING. Check the config and
        start until reaching STARTING_CARD_SWITCH, then wait for responses
        from player to switch cards.
        Returns:
            bool: True if success, False if error occurs.
            Any: If success, return None. Otherwise, return
                error message (str).
        """
        if self.state != MatchState.WAITING:
            error_message = (
                "Match is not waiting for start. If it is running "
                "or ended, please re-generate a new match."
            )
            logging.error(error_message)
            return False, error_message

        # make valid check
        if not self.config.check_config():
            error_message = "Match config is not valid."
            logging.error("Match config is not valid.")
            return False, error_message
        if len(self.player_tables) != 2:
            error_message = "Only support 2 players now."
            logging.error(error_message)
            return False, error_message
        for pnum, player_table in enumerate(self.player_tables):
            is_legal, info = player_table.player_deck_information.check_legal(
                card_number=self.config.card_number,
                max_same_card_number=self.config.max_same_card_number,
                character_number=self.config.character_number,
                check_restriction=self.config.check_deck_restriction,
            )
            if not is_legal:
                error_message = f"Player {pnum} deck is not legal. {info}"
                logging.error(error_message)
                return False, error_message

        self._set_match_state(MatchState.STARTING)

        # choose first player
        if self.config.random_first_player and not self.config.recreate_mode:
            self.current_player = int(self._random() > 0.5)
        else:
            self.current_player = self.config.player_go_first
        logging.info(f"Player {self.current_player} is the first player")

        # copy and randomize based on deck
        for pnum, player_table in enumerate(self.player_tables):
            # copy characters
            for cnum, character in enumerate(
                player_table.player_deck_information.characters
            ):
                character_copy = character.copy(deep=True)
                character_copy.position = ObjectPosition(
                    player_idx=pnum,
                    character_idx=cnum,
                    area=ObjectPositionType.CHARACTER,
                    id=character_copy.id,
                )
                character_copy.renew_id()
                for skill in character_copy.skills:
                    skill.renew_id()
                player_table.characters.append(character_copy)
            # copy cards
            if self.config.recreate_mode:
                # in recreate mode, do not shuffle cards, only copy to table
                # deck
                for card in player_table.player_deck_information.cards:
                    card_copy = card.copy(deep=True)
                    card_copy.position = ObjectPosition(
                        player_idx=pnum, area=ObjectPositionType.DECK, id=card_copy.id
                    )
                    card_copy.renew_id()
                    player_table.table_deck.append(card_copy)
            else:
                arcane_legend_cards = []
                for card in player_table.player_deck_information.cards:
                    card_copy = card.copy(deep=True)
                    card_copy.position = ObjectPosition(
                        player_idx=pnum, area=ObjectPositionType.DECK, id=card_copy.id
                    )
                    card_copy.renew_id()
                    if card_copy.type == ObjectType.ARCANE:
                        arcane_legend_cards.append(card_copy)
                    else:
                        player_table.table_deck.append(card_copy)
                if len(arcane_legend_cards):
                    # have arcane legend cards, they must in hand
                    if len(arcane_legend_cards) > self.config.initial_hand_size:
                        # shuffle arcane legend cards, and put over-maximum
                        # into table deck
                        self._random_shuffle(arcane_legend_cards)
                        player_table.table_deck += arcane_legend_cards[
                            self.config.initial_hand_size :
                        ]
                        arcane_legend_cards = arcane_legend_cards[
                            : self.config.initial_hand_size
                        ]
                # shuffle deck
                self._random_shuffle(player_table.table_deck)
                # prepend arcane legend cards
                player_table.table_deck = arcane_legend_cards + player_table.table_deck
            # add draw initial cards action
            event_args = self._act(
                DrawCardAction(
                    player_idx=pnum,
                    number=self.config.initial_hand_size,
                    draw_if_filtered_not_enough=False,
                )
            )
            event_frame = self.event_controller.stack_events(event_args)
            self.event_controller.append(event_frame)
        return True, None

    def step(self, run_continuously: bool = True) -> bool:
        """
        Simulate one step of the match, or run continuously until a response
        is needed from agents.

        Args:
            run_continuously (bool): If True, run continuously until a
                response is needed from agents. Otherwise, simulate one step
                and return. Default: True.

        Returns:
            bool: True if success, False if error occurs.
        """
        while True:
            # check if game reaches end condition
            if self.is_game_end():
                if self.state != MatchState.ENDED:  # pragma: no cover
                    self._set_match_state(MatchState.ENDED)
                    self._save_history()
                    return True
                else:
                    logging.error("Match has already ended.")
                    return False
            # check if it need response
            elif len(self.requests) != 0:
                logging.info("There are still requests not responded.")
                return False
            # check if action is needed
            elif self.event_controller.has_event():
                self.event_controller.run_event_frame(self)
            # all response and action are cleared, start state transition
            elif self.state == MatchState.STARTING:
                self._set_match_state(MatchState.STARTING_CARD_SWITCH)
                for player_idx in range(len(self.player_tables)):
                    self._request_switch_card(player_idx)
                if self.config.history_level > 0:
                    self._save_history()
            elif self.state == MatchState.STARTING_CARD_SWITCH:
                self._set_match_state(MatchState.STARTING_CHOOSE_CHARACTER)
                for player_idx in range(len(self.player_tables)):
                    self._request_choose_character(player_idx)
                if self.config.history_level > 0:
                    self._save_history()
            elif self.state == MatchState.STARTING_CHOOSE_CHARACTER:
                self._set_match_state(MatchState.GAME_START)
                self._game_start()
            elif self.state == MatchState.GAME_START:
                self._set_match_state(MatchState.ROUND_START)
                self._round_start()
            elif self.state == MatchState.ROUND_ROLL_DICE:
                self._set_match_state(MatchState.ROUND_PREPARING)
                self._round_prepare()
            elif self.state == MatchState.ROUND_PREPARING:
                self._set_match_state(MatchState.PLAYER_ACTION_START)
                self._player_action_start()
            elif self.state == MatchState.PLAYER_ACTION_START:
                self._set_match_state(MatchState.PLAYER_ACTION_REQUEST)
                self._player_action_request()
            elif self.state == MatchState.PLAYER_ACTION_REQUEST:
                # request responded and all action clear
                self._player_action_end()
            elif self.state == MatchState.ROUND_ENDING:
                self._set_match_state(MatchState.ROUND_ENDED)
                self._round_ending()
            elif self.state == MatchState.ROUND_ENDED:
                self._set_match_state(MatchState.ROUND_START)
                self._round_start()
            else:
                raise NotImplementedError(f"Match state {self.state} not implemented.")
            self.record_last_action_history()
            if self._debug_save_appeared_object_names:  # pragma: no cover
                self._debug_save_appeared_object_names_to_file()
            if len(self.requests) or not run_continuously:
                if len(self.requests):
                    logging.info(
                        f'{len(self.requests)} requests generated, '
                        f'{", ".join([req.name for req in self.requests])}'
                    )
                return True

    def check_request_exist(self, request: Requests) -> bool:
        """
        Check if the request is valid.
        """
        for req in self.requests:
            if req == request:
                return True
        return False

    def respond(self, response: Responses) -> None:
        """
        Deal with the response. When self.requests is not empty, at least one
        player should make response with this function based on requests.
        A player should choose all requests related to him and respond one of
        them. Different requests will use
        different respond function to deal with, and remove requests that do
        not need to respond or have responded.
        When respond is done, it will generate event frames. Once there is no
        request, Call `self.step()` to continue simulation.
        """
        logging.info(f"Response received: {response}")
        if len(self.requests) == 0:
            raise ValueError("Match is not waiting for response.")
        # check if the response is valid
        if not response.is_valid(self):
            raise ValueError("Response is not valid.")
        # check if the request exist
        if not self.check_request_exist(response.request):
            raise ValueError("Request does not exist.")
        # clear prediction after receiving response
        self.skill_predictions.clear()
        # call different respond functions based on the type of response
        if isinstance(response, SwitchCharacterResponse):
            self._respond_switch_character(response)
        elif isinstance(response, ElementalTuningResponse):
            self._respond_elemental_tuning(response)
        elif isinstance(response, DeclareRoundEndResponse):
            self._respond_declare_round_end(response)
        elif isinstance(response, UseSkillResponse):
            self._respond_use_skill(response)
        elif isinstance(response, UseCardResponse):
            self._respond_use_card(response)
        elif isinstance(response, SwitchCardResponse):
            self._respond_switch_card(response)
        elif isinstance(response, ChooseCharacterResponse):
            self._respond_choose_character(response)
        elif isinstance(response, RerollDiceResponse):
            self._respond_reroll_dice(response)
        else:
            raise AssertionError(f"Response type {type(response)} not recognized.")

    def is_game_end(self) -> bool:
        """
        Check if the game reaches end condition. If game is ended, it will
        set `self.winner` to the winner of the game.
        PVE may have different end condition with PVP, and currently not
        supported.

        Returns:
            bool: True if game reaches end condition, False otherwise.
        """
        # all characters are defeated
        for pnum, table in enumerate(self.player_tables):
            for character in table.characters:
                if character.is_alive:
                    break
            else:
                assert len(self.player_tables) == 2
                self.winner = 1 - pnum
                return True
        if self.round_number >= self.config.max_round_number:
            # reach max round number
            self.winner = -1
            return True
        return False

    def _game_start(self):
        """
        Game started. Will send game start event.
        """
        event = GameStartEventArguments(
            player_go_first=self.current_player,
        )
        self.event_controller.stack_event(event)

    def _round_start(self):
        """
        Start a round. Will clear existing dice, generate new random dice
        and asking players to reroll dice.
        """
        self.round_number += 1
        for table in self.player_tables:
            table.has_round_ended = False
        for pnum, player_table in enumerate(self.player_tables):
            player_table.dice.colors.clear()
        # generate new dice
        event_args: List[EventArguments] = []
        for pnum, player_table in enumerate(self.player_tables):
            initial_color_value = InitialDiceColorValue(
                player_idx=pnum,
                position=ObjectPosition(
                    player_idx=pnum,
                    area=ObjectPositionType.SYSTEM,
                    id=0,
                ),
            )
            self._modify_value(initial_color_value, "REAL")
            initial_color_value.dice_colors = initial_color_value.dice_colors[
                : self.config.initial_dice_number
            ]
            random_number = self.config.initial_dice_number - len(
                initial_color_value.dice_colors
            )
            color_dict: Dict[DieColor, int] = {}
            for color in initial_color_value.dice_colors:
                color_dict[color] = color_dict.get(color, 0) + 1
            for color, num in color_dict.items():
                event_args += self._act(
                    CreateDiceAction(player_idx=pnum, number=num, color=color)
                )
            event_args += self._act(
                CreateDiceAction(player_idx=pnum, number=random_number, random=True)
            )
        self.event_controller.stack_events(event_args)
        # collect actions triggered by round start
        # reroll dice chance. reroll times can be modified by objects.
        for pnum, player_table in enumerate(self.player_tables):
            reroll_times = self.config.initial_dice_reroll_times
            reroll_value = RerollValue(
                position=ObjectPosition(
                    player_idx=pnum,
                    area=ObjectPositionType.SYSTEM,
                    id=0,
                ),
                value=reroll_times,
                player_idx=pnum,
            )
            self._modify_value(reroll_value, mode="REAL")
            self._request_reroll_dice(pnum, reroll_value.value)
        self._set_match_state(MatchState.ROUND_ROLL_DICE)
        if self.config.history_level > 0:
            self._save_history()
        # can use GenerateRerollDiceRequest to generate reroll dice request
        # and add RoundStart event if needed

    def _round_prepare(self):
        """
        Activate round_prepare event, and add to actions.
        """
        event_arg = RoundPrepareEventArguments(
            player_go_first=self.current_player,
            round=self.round_number,
            dice_colors=[table.dice.colors.copy() for table in self.player_tables],
        )
        event_frame = self.event_controller.stack_event(event_arg)
        logging.info(
            f"In round prepare, {len(event_frame.triggered_objects)} "
            f"handlers triggered."
        )

    def _player_action_start(self):
        """
        Start a player's action phase. Will generate action phase start event.
        """
        not_all_declare_end = False
        for table in self.player_tables:
            if not table.has_round_ended:
                not_all_declare_end = True
        assert not_all_declare_end, "All players have declared round end."
        event = PlayerActionStartEventArguments(player_idx=self.current_player)
        self.event_controller.stack_event(event)

    def _player_action_request(self):
        """
        Will generate requests of available actions
        of the player. There will be the following actions:
        1. Use Skill: Pay the relevant cost and use your active character's
            Skill(s).
        2. Switch Characters: Pay 1 Elemental Die of your choice to switch your
            active character.
        3. Play Card: Pay the relevant cost and play card(s) from your Hand.
        4. Elemental Tuning: Discard a card from your Hand and change the
            Elemental Type of 1 of your Elemental Die which Elemental Type
            does not match your active character's Elemental Type, and also
            not Omni.
        5. Declare Round End: End your actions for this Round. The first player
            to declare the end of their Round will go first during the next
            Round.
        """
        # update charge condition
        table = self.player_tables[self.current_player]
        table.charge_satisfied = len(table.dice.colors) % 2 == 0
        # generate requests
        self._request_switch_character(self.current_player)
        self._request_elemental_tuning(self.current_player)
        self._request_declare_round_end(self.current_player)
        self._request_use_skill(self.current_player)
        self._request_use_card(self.current_player)
        self._predict_skill(self.current_player)
        if self.config.history_level > 0:
            self._save_history()

    def _player_action_end(self):
        """
        End a player's action phase. Will check status and go to proper state.
        """
        all_declare_end = True
        for table in self.player_tables:
            if not table.has_round_ended:
                all_declare_end = False
                break
        if all_declare_end:
            # all declare ended, go to round ending
            self._set_match_state(MatchState.ROUND_ENDING)
        else:
            # not all declare ended, go to next action
            # change to ROUND_PREPARING so will immediately transform to
            # PLAYER_ACTION_START in next step, and trigger corresponding event
            self._set_match_state(MatchState.ROUND_PREPARING)

    def _round_ending(self):
        """
        End a round. Will stack round end event.
        """
        event = RoundEndEventArguments(
            player_go_first=self.current_player,
            round=self.round_number,
            initial_card_draw=self.config.initial_card_draw,
        )
        self.event_controller.stack_event(event)

    def get_object(
        self, position: ObjectPosition, action: ActionTypes | None = None
    ) -> ObjectBase | None:
        """
        Get object by its position. If object not exist, return None.
        When action is specified, it will check trashbin and find objects that
        can handle the action.
        """
        assert position.area != ObjectPositionType.INVALID, "Invalid area."
        if position.area == ObjectPositionType.SYSTEM:
            for object in self.event_handlers:
                if object.id == position.id:
                    return object
            raise NotImplementedError("Currently should not be None")
        res = self.player_tables[position.player_idx].get_object(position)
        if res is None and action is not None:
            # not found, try to find in trashbin
            for object in self.trashbin:
                if (
                    object.position.id == position.id
                    and action in object.available_handler_in_trashbin
                ):
                    return object
        return res

    def get_object_list(self) -> List[ObjectBase]:
        """
        Get all objects in the match by `self.table.get_object_lists`.
        The order of objects should follow the game rule. The rules are:
        1. objects of `self.current_player` goes first
        2. objects belongs to character and team status goes first
            2.1. active character first, then next, next ... until all alive
                characters are included.
            2.2. for one character, order is character self, its skills, other objects
                attached to the character.
            2.3. status and equipment have no priority, just based on the time when they
                are attached to the character.
            2.4. specifically, team status has lower priority of active character and
                its attached objects, but higher priority of other characters.
        3. for other objects, order is: summon, support, hand, dice, deck.
            3.1. all other objects in same region are sorted by their index in
                the list.
        4. system event handler
        """
        return (
            self.player_tables[self.current_player].get_object_lists()
            + self.player_tables[1 - self.current_player].get_object_lists()
            + self.event_handlers
        )

    def _modify_value(
        self,
        value: ModifiableValueBase,
        mode: Literal["TEST", "REAL"],
    ) -> None:
        """
        Modify values. It will modify the value argument in-place.
        Args:
            value (ModifiableValues): The value to be modified. It contains
                value itself and all necessary information to modify the value.
            potision (ObjectPosition): The position of the object that the
                value is based on.
            mode (Literal['test', 'real']): If 'test', objects will only modify
                the value but not updating inner state, which is used to
                calculate costs used in requests. If 'real', it will modify
                the value and update inner state, which means the request
                related to the value is executed.
        """
        if mode == "TEST":
            assert value.type in [
                ModifiableValueTypes.COST,
                ModifiableValueTypes.FULL_COST,
            ], "Only costs can be modified in test mode."
        object_list = self.get_object_list()
        modifier_name = f"value_modifier_{value.type.name}"
        for obj in object_list:
            name = obj.__class__.__name__
            if hasattr(obj, "name"):  # pragma: no cover
                name = obj.name  # type: ignore
            func = getattr(obj, modifier_name, None)
            if func is not None:
                logging.debug(f"Modify value {value.type.name} for {name}.")
                value = func(value, self, mode)

    def _modify_cost_value(
        self,
        cost_value: CostValue,
        mode: Literal["TEST", "REAL"],
    ) -> FullCostValue:
        self._modify_value(cost_value, mode)
        full_cost_value = FullCostValue.from_cost_value(cost_value)
        self._modify_value(full_cost_value, mode)
        return full_cost_value

    def _predict_skill(self, player_idx: int) -> None:
        """
        Predict skill results of a player. If config.make_skill_prediction,
        it will predict the results when a skill is used, regardless of the
        skill availability, except for skills that can never be used by player.
        The predict results are saved in self.skill_predictions, with the
        player idx, character idx, skill idx, and diff of the match after
        using the skill.
        """
        self.skill_predictions = []
        if not self.config.make_skill_prediction or self._prediction_mode:
            # do not predict
            return
        # get copy of current match, but except histories.
        history = self._history[:]
        history_diff = self._history_diff[:]
        self._history.clear()
        self._history_diff.clear()
        copy = self.copy(deep=True, exclude={"_history", "_history_diff"})
        self._history += history
        self._history_diff += history_diff
        # disable history logging and skill prediction for copy
        copy._prediction_mode = True
        table = copy.player_tables[player_idx]
        character = table.characters[table.active_character_idx]
        skills = character.skills
        for sidx, skill in enumerate(skills):
            if not skill.is_valid(self):
                continue
            # a valid skill, try to use it
            one_copy = copy.copy(deep=True)
            one_copy._respond_use_skill(
                UseSkillResponse(
                    request=UseSkillRequest(
                        player_idx=player_idx,
                        character_idx=table.active_character_idx,
                        skill_idx=sidx,
                        dice_colors=[],
                        cost=Cost(original_value=Cost()),
                    ),
                    dice_idxs=[],
                )
            )
            one_copy.step()
            # get diff after prediction
            diff = list(dictdiffer.diff(copy.dict(), one_copy.dict()))
            # remove prev values of 'remove' in diff
            for d in diff:
                if d[0] == "remove":
                    for i in range(len(d[2])):
                        d[2][i] = (d[2][i][0], None)
            self.skill_predictions.append(
                {
                    "player_idx": player_idx,
                    "character_idx": table.active_character_idx,
                    "skill_idx": sidx,
                    "diff": diff,
                }
            )

    """
    Request functions. To generate specific requests.
    """

    def _request_switch_card(self, player_idx: int):
        """
        Generate switch card requests.
        """
        table = self.player_tables[player_idx]
        self.requests.append(
            SwitchCardRequest(
                player_idx=player_idx, card_names=[card.name for card in table.hands]
            )
        )

    def _request_choose_character(self, player_idx: int):
        """
        Generate switch card requests.
        """
        table = self.player_tables[player_idx]
        available: List[int] = []
        for cnum, character in enumerate(table.characters):
            if character.is_alive:
                available.append(cnum)
        self.requests.append(
            ChooseCharacterRequest(
                player_idx=player_idx, available_character_idxs=available
            )
        )

    def _request_reroll_dice(self, player_idx: int, reroll_number: int):
        """
        reroll by game actions cannot be modified
        """
        if reroll_number <= 0:
            return
        player_table = self.player_tables[player_idx]
        self.requests.append(
            RerollDiceRequest(
                player_idx=player_idx,
                colors=player_table.dice.colors.copy(),
                reroll_times=reroll_number,
            )
        )

    def _request_switch_character(self, player_idx: int):
        """
        Generate switch character requests.
        """
        table = self.player_tables[player_idx]
        active_character = table.characters[table.active_character_idx]
        for cidx, character in enumerate(table.characters):
            if cidx == table.active_character_idx or character.is_defeated:
                continue
            dice_cost = Cost(any_dice_number=1)
            dice_cost.label = CostLabels.SWITCH_CHARACTER.value
            dice_cost_value = CostValue(
                cost=dice_cost,
                position=active_character.position,
                target_position=character.position,
            )
            dice_cost_value = self._modify_cost_value(dice_cost_value, mode="TEST")
            charge, arcane_legend = table.get_charge_and_arcane_legend()
            if not dice_cost_value.cost.is_valid(
                dice_colors=table.dice.colors,
                charge=charge,
                arcane_legend=arcane_legend,
                strict=False,
            ):
                continue
            self.requests.append(
                SwitchCharacterRequest(
                    player_idx=player_idx,
                    active_character_idx=table.active_character_idx,
                    target_character_idx=cidx,
                    dice_colors=table.dice.colors.copy(),
                    cost=dice_cost_value.cost,
                )
            )

    def _request_elemental_tuning(self, player_idx: int):
        table = self.player_tables[player_idx]
        target_color = ELEMENT_TO_DIE_COLOR[
            table.characters[table.active_character_idx].element
        ]
        available_dice_idx = [
            didx
            for didx, color in enumerate(table.dice.colors)
            if color != target_color and color != DieColor.OMNI
        ]
        if self.config.recreate_mode:
            # in recreate mode, all dice can be tuned
            available_dice_idx = list(range(len(table.dice.colors)))
        available_card_idxs = list(range(len(table.hands)))
        if len(available_dice_idx) and len(available_card_idxs):
            self.requests.append(
                ElementalTuningRequest(
                    player_idx=player_idx,
                    dice_colors=table.dice.colors.copy(),
                    dice_idxs=available_dice_idx,
                    card_idxs=available_card_idxs,
                )
            )

    def _request_declare_round_end(self, player_idx: int):
        self.requests.append(DeclareRoundEndRequest(player_idx=player_idx))

    def _request_use_skill(self, player_idx: int):
        """
        Generate use skill requests. If active character is stunned, or
        not satisfy the condition to use skill, it will skip generating
        request.
        """
        table = self.player_tables[player_idx]
        front_character = table.characters[table.active_character_idx]
        if front_character.is_stunned:
            # stunned, cannot use skill.
            return
        for sid, skill in enumerate(front_character.skills):
            if skill.is_valid(self):
                cost = skill.cost.copy()
                if (
                    skill.skill_type == SkillType.NORMAL_ATTACK
                    and table.charge_satisfied
                ):
                    # normal attack and satisfy charge, charge attack.
                    cost.label |= CostLabels.CHARGED_ATTACK.value
                if (
                    skill.skill_type == SkillType.NORMAL_ATTACK
                    and table.plunge_satisfied
                ):
                    # normal attack and satisfy plunge, plunge attack.
                    cost.label |= CostLabels.PLUNGING_ATTACK.value
                cost_value = CostValue(
                    cost=cost, position=skill.position, target_position=None
                )
                cost_value = self._modify_cost_value(cost_value, "TEST")
                dice_colors = table.dice.colors
                if cost_value.cost.is_valid(
                    dice_colors=dice_colors,
                    charge=front_character.charge,
                    arcane_legend=table.arcane_legend,
                    strict=False,
                ):
                    self.requests.append(
                        UseSkillRequest(
                            player_idx=player_idx,
                            character_idx=table.active_character_idx,
                            skill_idx=sid,
                            dice_colors=dice_colors.copy(),
                            cost=cost_value.cost,
                        )
                    )

    def _request_use_card(self, player_idx: int):
        table = self.player_tables[player_idx]
        cards = table.hands
        for cid, card in enumerate(cards):
            if card.is_valid(self):
                cost = card.cost.copy()
                cost_value = CostValue(
                    cost=cost, position=card.position, target_position=None
                )
                cost_value = self._modify_cost_value(cost_value, "TEST")
                dice_colors = table.dice.colors
                charge, arcane_legend = table.get_charge_and_arcane_legend()
                if cost_value.cost.is_valid(
                    dice_colors=dice_colors,
                    charge=charge,
                    arcane_legend=arcane_legend,
                    strict=False,
                ):
                    self.requests.append(
                        UseCardRequest(
                            player_idx=player_idx,
                            card_idx=cid,
                            dice_colors=dice_colors.copy(),
                            cost=cost_value.cost,
                            targets=list(card.get_targets(self)),
                        )
                    )

    """
    Response functions. To deal with specific responses.
    """

    def _respond_switch_card(self, response: SwitchCardResponse):
        if self.version <= "0.0.4":
            return self._respond_switch_card_004(response)
        return self._respond_switch_card_005(response)

    def _respond_switch_card_005(self, response: SwitchCardResponse):
        """
        New version, using SwitchCardAction.
        """
        event_args = self._act(
            SwitchCardAction(
                player_idx=response.player_idx,
                restore_card_idxs=response.card_idxs,
            )
        )
        event_frame = self.event_controller.stack_events(event_args)
        self.event_controller.append(event_frame)
        # remove related requests
        self.requests = [
            req for req in self.requests if req.player_idx != response.player_idx
        ]

    def _respond_switch_card_004(self, response: SwitchCardResponse):
        """
        Deal with switch card response.
        """
        # restore cards
        event_args: List[EventArguments] = []
        event_args += self._act(
            RestoreCardAction(
                player_idx=response.player_idx, card_idxs=response.card_idxs
            )
        )
        event_args += self._act(
            DrawCardAction(
                player_idx=response.player_idx,
                number=len(response.card_idxs),
                blacklist_names=response.card_names,
                draw_if_filtered_not_enough=True,
            )
        )
        event_frame = self.event_controller.stack_events(event_args)
        self.event_controller.append(event_frame)
        # remove related requests
        self.requests = [
            req for req in self.requests if req.player_idx != response.player_idx
        ]

    def _respond_choose_character(self, response: ChooseCharacterResponse):
        event_args = self._act(ChooseCharacterAction.from_response(response))
        self.event_controller.stack_events(event_args)
        # remove related requests
        self.requests = [
            req for req in self.requests if req.player_idx != response.player_idx
        ]

    def _respond_reroll_dice(self, response: RerollDiceResponse):
        """
        Deal with reroll dice response. If there are still reroll times left,
        keep request and only substrat reroll times. If there are no reroll
        times left, remove request.
        """
        event_args = self._action_remove_dice(RemoveDiceAction.from_response(response))
        event_frame = self.event_controller.stack_events(list(event_args))
        self.event_controller.append(event_frame)
        event_args = self._action_create_dice(
            CreateDiceAction(
                player_idx=response.player_idx,
                number=len(response.reroll_dice_idxs),
                random=True,
            )
        )
        event_frame = self.event_controller.stack_events(list(event_args))
        self.event_controller.append(event_frame)
        # modify request
        for num, req in enumerate(self.requests):  # pragma: no branch
            if isinstance(req, RerollDiceRequest):  # pragma: no branch
                if req.player_idx == response.player_idx:  # pragma: no branch
                    if req.reroll_times > 1:
                        req.reroll_times -= 1
                        req.colors = self.player_tables[
                            response.player_idx
                        ].dice.colors.copy()
                    else:
                        self.requests.pop(num)
                    break

    def _respond_switch_character(self, response: SwitchCharacterResponse):
        """
        Deal with switch character response. If it is combat action, add
        combat action to action queue. Remove related requests.
        """
        actions: List[ActionBase] = []
        dice_idxs = response.dice_idxs
        if len(dice_idxs):
            actions.append(
                RemoveDiceAction(
                    player_idx=response.player_idx,
                    dice_idxs=dice_idxs,
                )
            )
        table = self.player_tables[response.player_idx]
        active_character = table.characters[table.active_character_idx]
        target_characters = table.characters[response.request.target_character_idx]
        cost = response.request.cost.original_value
        assert cost is not None
        cost_value = CostValue(
            position=active_character.position,
            cost=cost,
            target_position=target_characters.position,
        )
        cost_value = self._modify_cost_value(cost_value, "REAL")
        actions.append(SwitchCharacterAction.from_response(response))
        end_action = ActionEndAction(
            action_label=PlayerActionLabels.SWITCH.value,
            position=ObjectPosition(
                player_idx=response.player_idx,
                character_idx=response.request.active_character_idx,
                area=ObjectPositionType.CHARACTER,
                id=self.player_tables[response.player_idx]
                .characters[response.request.active_character_idx]
                .id,
            ),
            do_combat_action=True,
        )
        # as after switching character, the active character may change, so
        # we need to update combat action value before switching.
        combat_action_value = CombatActionValue(
            position=end_action.position,
            action_label=end_action.action_label,
            do_combat_action=end_action.do_combat_action,
        )
        self._modify_value(value=combat_action_value, mode="REAL")
        end_action.do_combat_action = combat_action_value.do_combat_action
        actions.append(end_action)
        self.event_controller.stack_actions(actions)
        self.requests = [
            x for x in self.requests if x.player_idx != response.player_idx
        ]

    def _respond_elemental_tuning(self, response: ElementalTuningResponse):
        """
        Deal with elemental tuning response. It is split into 3 actions,
        remove one hand card, remove one die, and add one die.
        """
        die_idx = response.dice_idx
        table = self.player_tables[response.player_idx]
        actions: List[ActionBase] = []
        actions.append(
            RemoveCardAction(
                position=table.hands[response.card_idx].position, remove_type="BURNED"
            )
        )
        actions.append(
            RemoveDiceAction(player_idx=response.player_idx, dice_idxs=[die_idx])
        )
        active_character = table.get_active_character()
        assert active_character is not None
        actions.append(
            CreateDiceAction(
                player_idx=response.player_idx,
                number=1,
                color=ELEMENT_TO_DIE_COLOR[active_character.element],
            )
        )
        actions.append(
            ActionEndAction(
                action_label=PlayerActionLabels.TUNE.value,
                position=ObjectPosition(
                    player_idx=response.player_idx, area=ObjectPositionType.SYSTEM, id=0
                ),
                do_combat_action=False,
            )
        )
        self.event_controller.stack_actions(actions)
        self.requests = [
            x for x in self.requests if x.player_idx != response.player_idx
        ]

    def _respond_declare_round_end(self, response: DeclareRoundEndResponse):
        """
        Deal with declare round end response. It is split into 2 actions,
        declare round end and combat action.
        """
        actions: List[ActionBase] = []
        actions.append(DeclareRoundEndAction.from_response(response))
        actions.append(
            ActionEndAction(
                action_label=PlayerActionLabels.END.value,
                position=ObjectPosition(
                    player_idx=response.player_idx, area=ObjectPositionType.SYSTEM, id=0
                ),
                do_combat_action=True,
            )
        )
        self.event_controller.stack_actions(actions)
        self.requests = [
            x for x in self.requests if x.player_idx != response.player_idx
        ]

    def _respond_use_skill(self, response: UseSkillResponse):
        request = response.request
        skill = (
            self.player_tables[response.player_idx]
            .characters[request.character_idx]
            .skills[request.skill_idx]
        )
        cost = response.request.cost.original_value
        assert cost is not None
        cost_value = CostValue(position=skill.position, cost=cost, target_position=None)
        cost_value = self._modify_cost_value(cost_value, "REAL")
        action_label, combat_action = skill.get_action_type(self)
        actions: List[Actions] = [
            RemoveDiceAction(
                player_idx=response.player_idx,
                dice_idxs=response.dice_idxs,
            ),
            UseSkillAction(
                skill_position=skill.position,
            ),
            SkillEndAction(
                position=skill.position,
                target_position=self.player_tables[1 - skill.position.player_idx]
                .get_active_character()
                .position,
                skill_type=skill.skill_type,
            ),
            ActionEndAction(
                action_label=action_label,
                position=skill.position,
                do_combat_action=combat_action,
            ),
        ]
        self.event_controller.stack_actions(actions)
        self.requests = [
            x for x in self.requests if x.player_idx != response.player_idx
        ]

    def _respond_use_card(self, response: UseCardResponse):
        request = response.request
        table = self.player_tables[response.player_idx]
        card = table.hands[request.card_idx]
        cost = response.request.cost.original_value
        assert cost is not None
        cost_value = CostValue(position=card.position, cost=cost, target_position=None)
        cost_value = self._modify_cost_value(cost_value, "REAL")
        actions: List[Actions] = [
            RemoveDiceAction(
                player_idx=response.player_idx,
                dice_idxs=response.dice_idxs,
            ),
            UseCardAction(
                card_position=card.position,
                target=response.target,
            ),
        ]
        action_label, combat_action = card.get_action_type(self)
        actions.append(
            ActionEndAction(
                action_label=action_label,
                position=card.position,
                do_combat_action=combat_action,
            )
        )
        self.event_controller.stack_actions(actions)
        self.requests = [
            x for x in self.requests if x.player_idx != response.player_idx
        ]

    """
    Action Functions
    """

    def _act(self, action: ActionBase) -> List[EventArguments]:
        """
        Act an action. It will call corresponding action function based on
        the type of the action.

        Action functions take Action as input, do
        changes of the game table, and return a list of triggered events.
        In most case, the list should contain exactly one event argument,
        however we use list to make it compatible with future changes.

        Returns:
            A list of triggered event arguments. We wrap the returned event
            arguments of action functions in a list to avoid error from linter.
        """
        self.last_action = action
        self.action_info = {}
        if isinstance(action, ChooseCharacterAction):
            return list(self._action_choose_character(action))
        elif isinstance(action, CreateDiceAction):
            return list(self._action_create_dice(action))
        elif isinstance(action, RemoveDiceAction):
            return list(self._action_remove_dice(action))
        elif isinstance(action, RestoreCardAction):
            return list(self._action_restore_card(action))
        elif isinstance(action, DrawCardAction):
            return list(self._action_draw_card(action))
        elif isinstance(action, RemoveCardAction):
            return list(self._action_remove_card(action))
        elif isinstance(action, SwitchCardAction):
            return list(self._action_switch_card(action))
        elif isinstance(action, SwitchCharacterAction):
            return list(self._action_switch_character(action))
        elif isinstance(action, DeclareRoundEndAction):
            return list(self._action_declare_round_end(action))
        elif isinstance(action, ActionEndAction):
            return list(self._action_action_end(action))
        elif isinstance(action, MakeDamageAction):
            return list(self._action_make_damage(action))
        elif isinstance(action, ChargeAction):
            return list(self._action_charge(action))
        elif isinstance(action, UseSkillAction):
            return list(self._action_use_skill(action))
        elif isinstance(action, UseCardAction):
            return list(self._action_use_card(action))
        elif isinstance(action, SkillEndAction):
            return list(self._action_skill_end(action))
        elif isinstance(action, CharacterDefeatedAction):
            return list(self._action_character_defeated(action))
        elif isinstance(action, CreateObjectAction):
            return list(self._action_create_object(action))
        elif isinstance(action, CreateRandomObjectAction):
            return list(self._action_create_random_object(action))
        elif isinstance(action, RemoveObjectAction):
            return list(self._action_remove_object(action))
        elif isinstance(action, ChangeObjectUsageAction):
            return list(self._action_change_object_usage(action))
        elif isinstance(action, MoveObjectAction):
            return list(self._action_move_object(action))
        elif isinstance(action, ConsumeArcaneLegendAction):
            return list(self._action_consume_arcane_legend(action))
        elif isinstance(action, GenerateChooseCharacterRequestAction):
            return list(self._action_generate_choose_character_request(action))
        elif isinstance(action, GenerateRerollDiceRequestAction):
            return list(self._action_generate_reroll_dice_request(action))
        elif isinstance(action, SkipPlayerActionAction):
            return list(self._action_skip_player_action(action))
        elif isinstance(action, CharacterReviveAction):
            return list(self._action_character_revive(action))
        elif isinstance(action, GenerateSwitchCardRequestAction):
            return list(self._action_generate_switch_card_request(action))
        else:
            self._set_match_state(MatchState.ERROR)  # pragma no cover
            raise AssertionError(f"Unknown action {action}.")

    def _action_draw_card(self, action: DrawCardAction) -> List[DrawCardEventArguments]:
        """
        Draw cards from the deck, and return the argument of triggered events.
        Can set blacklist or whitelist to filter cards. Cannot set both.
        If writelist is set, card should satisfy all whitelists.
        If blacklist is set, card should satisfy no blacklist.
        If available cards are less than number, draw all available cards,
        and if draw_if_not_enough is set True, randomly draw cards until
        number is reached or deck is empty.
        """
        if self.version <= "0.0.4":
            return self._action_draw_card_004(action)
        return self._action_draw_card_005(action)

    def _action_draw_card_005(
        self, action: DrawCardAction
    ) -> List[DrawCardEventArguments]:
        """
        When no list set, just draw cards. When whitelist set, will find all cards
        that satisfy the whitelist, and randomly draw from them. When blacklist set,
        will draw cards from top to bottom that not blacklist-ed. If not enough and
        draw_if_filtered_not_enough is set, will draw from blacklist cards, and this
        is not allowed when using whitelist.
        """
        player_idx = action.player_idx
        number = action.number
        table = self.player_tables[player_idx]
        deck = table.table_deck
        target_card_idxs: list[int] = []
        if (
            action.whitelist_cost_labels > 0
            or len(action.whitelist_names) > 0
            or len(action.whitelist_types) > 0
        ):
            if (
                action.blacklist_cost_labels > 0
                or len(action.blacklist_names) > 0
                or len(action.blacklist_types) > 0
            ):
                self._set_match_state(MatchState.ERROR)
                raise AssertionError(
                    "Whitelist and blacklist cannot be both specified."
                )
            if action.draw_if_filtered_not_enough:
                self._set_match_state(MatchState.ERROR)
                raise AssertionError(
                    "Cannot draw_if_filtered_not_enough when whitelist is set."
                )
            # whitelist set
            for idx, card in enumerate(table.table_deck):
                if (
                    card.cost_label & action.whitelist_cost_labels != 0
                    or card.name in action.whitelist_names
                    or card.type in action.whitelist_types
                ):
                    target_card_idxs.append(idx)
            if self.config.recreate_mode:
                # in recreate mode, just select top cards
                for i in range(number):
                    assert i in target_card_idxs, (
                        f"Card {deck[i].name}:{i} should be in whitelist in recreate "
                        "mode, but not found"
                    )
            else:
                # otherwise, shuffle target and pick number cards
                self._random_shuffle(target_card_idxs)
            target_card_idxs = target_card_idxs[:number]
        elif (
            action.blacklist_cost_labels > 0
            or len(action.blacklist_names) > 0
            or len(action.blacklist_types) > 0
        ):
            # blacklist set
            black_card_idxs: list[int] = []
            for idx, card in enumerate(table.table_deck):
                if (
                    card.cost_label & action.blacklist_cost_labels == 0
                    and card.name not in action.blacklist_names
                    and card.type not in action.blacklist_types
                ):
                    target_card_idxs.append(idx)
                else:
                    black_card_idxs.append(idx)
            if self.config.recreate_mode:
                raise NotImplementedError("Not tested")
                # in recreate mode, just select top cards
                for i in range(number):
                    assert i in target_card_idxs, (
                        f"Card {deck[i].name}:{i} should not be in blacklist in "
                        "recreate mode, but found"
                    )
            if len(target_card_idxs) < number and action.draw_if_filtered_not_enough:
                # draw blacklist cards
                length = number - len(target_card_idxs)
                target_card_idxs += black_card_idxs[:length]
                black_card_idxs = black_card_idxs[length:]
            target_card_idxs = target_card_idxs[:number]
        else:
            # no filter
            target_card_idxs = list(range(min(len(deck), number)))
        new_deck: list[CardBase] = []
        drawn_cards: list[CardBase] = []
        for idx, card in enumerate(table.table_deck):
            if idx in target_card_idxs:
                drawn_cards.append(card)
            else:
                new_deck.append(card)
        table.table_deck = new_deck
        names = [x.name for x in drawn_cards]
        for card in drawn_cards:
            card.position = card.position.set_area(ObjectPositionType.HAND)
        table.hands.extend(drawn_cards)
        logging.info(
            f"Draw card action, player {player_idx}, number {number}, "
            f"cards {names}, "
            f"deck size {len(table.table_deck)}, hand size {len(table.hands)}"
        )
        event_arg = DrawCardEventArguments(
            action=action,
            hand_size=len(table.hands),
            max_hand_size=self.config.max_hand_size,
        )
        return [event_arg]

    def _action_draw_card_004(
        self, action: DrawCardAction
    ) -> List[DrawCardEventArguments]:
        """
        In old versions, the order of cards in deck will be changed if using filters.
        In new versions, the order will not change, and _action_draw_card_005 is used.
        """
        player_idx = action.player_idx
        number = action.number
        table = self.player_tables[player_idx]
        if len(table.table_deck) < number:
            number = len(table.table_deck)
        draw_cards: List[CardBase] = []
        blacklist: List[CardBase] = []
        if self.version <= "0.0.1":
            # in 0.0.1, whitelist and blacklist are not supported
            # no filter
            draw_cards = table.table_deck[:number]
            table.table_deck = table.table_deck[number:]
        elif (
            action.whitelist_cost_labels > 0
            or len(action.whitelist_names) > 0
            or len(action.whitelist_types) > 0
        ):
            if (
                action.blacklist_cost_labels > 0
                or len(action.blacklist_names) > 0
                or len(action.blacklist_types) > 0
            ):
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise AssertionError(
                    "Whitelist and blacklist cannot be both " "specified."
                )
            # whitelist set
            while len(table.table_deck) > 0 and len(draw_cards) < number:
                card = table.table_deck.pop(0)
                if (
                    card.cost_label & action.whitelist_cost_labels != 0
                    or card.name in action.whitelist_names
                    or card.type in action.whitelist_types
                ):
                    draw_cards.append(card)
                else:
                    blacklist.append(card)
            assert not self.config.recreate_mode or len(blacklist) == 0, (
                "Blacklist should be empty in recreate mode. Please check "
                "card order."
            )
            if len(draw_cards) < number and action.draw_if_filtered_not_enough:
                # draw blacklist cards
                length = number - len(draw_cards)
                draw_cards += blacklist[:length]
                blacklist = blacklist[length:]
        elif (
            action.blacklist_cost_labels > 0
            or len(action.blacklist_names) > 0
            or len(action.blacklist_types) > 0
        ):
            # blacklist set
            while len(table.table_deck) > 0 and len(draw_cards) < number:
                card = table.table_deck.pop(0)
                if (
                    card.cost_label & action.blacklist_cost_labels == 0
                    and card.name not in action.blacklist_names
                    and card.type not in action.blacklist_types
                ):
                    draw_cards.append(card)
                else:
                    blacklist.append(card)
            assert not self.config.recreate_mode or len(blacklist) == 0, (
                "Blacklist should be empty in recreate mode. Please check "
                "card order."
            )
            if len(draw_cards) < number and action.draw_if_filtered_not_enough:
                # draw blacklist cards
                length = number - len(draw_cards)
                draw_cards += blacklist[:length]
                blacklist = blacklist[length:]
        else:
            # no filter
            draw_cards = table.table_deck[:number]
            table.table_deck = table.table_deck[number:]
        if len(blacklist):
            table.table_deck += blacklist
            self._random_shuffle(table.table_deck)
        names = [x.name for x in draw_cards]
        for card in draw_cards:
            card.position = card.position.set_area(ObjectPositionType.HAND)
        table.hands.extend(draw_cards)
        logging.info(
            f"Draw card action, player {player_idx}, number {number}, "
            f"cards {names}, "
            f"deck size {len(table.table_deck)}, hand size {len(table.hands)}"
        )
        event_arg = DrawCardEventArguments(
            action=action,
            hand_size=len(table.hands),
            max_hand_size=self.config.max_hand_size,
        )
        return [event_arg]

    def _action_restore_card(
        self, action: RestoreCardAction
    ) -> List[RestoreCardEventArguments]:
        """
        Restore cards to the deck. It will be put into random position of deck.
        Before 0.0.5, the order of original cards may be changed after restore, after
        0.0.5, the order of original cards will not change.
        """
        if self.version <= "0.0.4":
            return self._action_restore_card_004(action)
        return self._action_restore_card_005(action)

    def _action_restore_card_005(
        self, action: RestoreCardAction
    ) -> List[RestoreCardEventArguments]:
        """
        Restore cards to the deck. It will be put into random position of deck.
        The order of original cards will not change, but the order of restored cards
        will be random.
        If recreate mode is on, all cards will be put at bottom of deck without shuffle.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        number_after_restore: int = len(action.card_idxs) + len(table.table_deck)
        numbers = list(range(number_after_restore))
        if len(action.card_idxs) == 0:
            # nothing to do
            logging.info(
                f"Restore card action, player {action.player_idx}, "
                f"number 0, deck size {len(table.table_deck)}, "
                f"hand size {len(table.hands)}"
            )
            return [RestoreCardEventArguments(action=action, card_names=[])]
        if not self.config.recreate_mode:  # pragma: no branch
            # if not recreate mode, shuffle the numbers
            self._random_shuffle(numbers)
            action.card_idxs.sort()
            self._random_shuffle(action.card_idxs)
        numbers = numbers[-len(action.card_idxs) :]  # restored card positions in deck
        new_hand = []
        restored_cards = []
        new_deck = []
        for idx in action.card_idxs:
            restored_cards.append(table.hands[idx])
        for idx, card in enumerate(table.hands):
            if idx not in action.card_idxs:
                new_hand.append(card)
        for card in restored_cards:
            card.position = card.position.set_area(ObjectPositionType.DECK)
        card_names = [x.name for x in restored_cards]
        for new_deck_idx in range(number_after_restore):
            if new_deck_idx in numbers:
                new_deck.append(restored_cards.pop(0))
            else:
                new_deck.append(table.table_deck.pop(0))
        table.hands = new_hand
        table.table_deck = new_deck
        logging.info(
            f"Restore card action, player {player_idx}, "
            f"number {len(action.card_idxs)}, cards: {card_names}, "
            f"deck size {len(table.table_deck)}, hand size {len(table.hands)}"
        )
        event_arg = RestoreCardEventArguments(action=action, card_names=card_names)
        return [event_arg]

    def _action_restore_card_004(
        self, action: RestoreCardAction
    ) -> List[RestoreCardEventArguments]:
        """
        Restore cards to the deck.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        card_idxs = action.card_idxs[:]
        card_idxs.sort(reverse=True)  # reverse order to avoid index error
        card_names = [table.hands[cidx].name for cidx in card_idxs]
        restore_cards: List[CardBase] = []
        for cidx in card_idxs:
            restore_cards.append(table.hands[cidx])
            table.hands = table.hands[:cidx] + table.hands[cidx + 1 :]
        for card in restore_cards:
            card.position = card.position.set_area(ObjectPositionType.DECK)
        table.table_deck.extend(restore_cards)
        if self.version >= "0.0.2" and not self.config.recreate_mode:
            # after 0.0.2, deck is shuffled after restore cards
            self._random_shuffle(table.table_deck)
        logging.info(
            f"Restore card action, player {player_idx}, "
            f"number {len(card_idxs)}, cards: {card_names}, "
            f"deck size {len(table.table_deck)}, hand size {len(table.hands)}"
        )
        event_arg = RestoreCardEventArguments(action=action, card_names=card_names)
        return [event_arg]

    def _action_switch_card(
        self, action: SwitchCardAction
    ) -> List[
        SwitchCardEventArguments | DrawCardEventArguments | RestoreCardEventArguments
    ]:
        """
        Switch card from hand to deck. It will be put into random position of deck.
        It is implemented by calling restore card and draw card.

        It will return three events, one for switch card, one for restore card,
        and one for draw card.
        """
        table = self.player_tables[action.player_idx]
        restore_action = RestoreCardAction(
            player_idx=action.player_idx, card_idxs=action.restore_card_idxs
        )
        card_names = [table.hands[x].name for x in action.restore_card_idxs]
        draw_action = DrawCardAction(
            player_idx=action.player_idx,
            number=len(action.restore_card_idxs),
            blacklist_names=card_names,
            draw_if_filtered_not_enough=True,
        )
        restore_event_arg = self._action_restore_card(restore_action)
        draw_event_arg = self._action_draw_card(draw_action)
        return [
            SwitchCardEventArguments(
                action=action,
                switch_number=len(action.restore_card_idxs),
                restore_card_event=restore_event_arg[0],
                draw_card_event=draw_event_arg[0],
            )
        ]

    def _action_remove_card(
        self, action: RemoveCardAction
    ) -> List[RemoveCardEventArguments]:
        player_idx = action.position.player_idx
        card_position = action.position.area
        card_id = action.position.id
        remove_type = action.remove_type  # used or burned (Keqing, EleTuning)
        table = self.player_tables[player_idx]
        if table.using_hand is not None and card_id == table.using_hand.id:
            card = table.using_hand
            table.using_hand = None
        elif card_position == ObjectPositionType.HAND:
            match_idx = -1
            for idx, card in enumerate(table.hands):
                if card.id == card_id:
                    match_idx = idx
                    break
            else:
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise AssertionError(f"Cannot find card {card_id} in hand.")
            card = table.hands.pop(match_idx)
        # elif card_position == ObjectPositionType.DECK:
        #     card = table.table_deck.pop(action.card_idx)
        else:
            self._set_match_state(MatchState.ERROR)  # pragma no cover
            raise AssertionError(f"Unknown card position {card_position}.")
        logging.info(
            f"Remove hand card action, player {player_idx}, "
            f"card position {card_position}, "
            f"card name {card.name}, "
            f"remove type {remove_type}."
        )
        event_arg = RemoveCardEventArguments(action=action, card_name=card.name)
        return [event_arg]

    def _action_choose_character(
        self, action: ChooseCharacterAction
    ) -> List[ChooseCharacterEventArguments]:
        """
        This action triggers by game start and by active character is defeated.
        Be care of differences between choose_character when implementing
        event triggers.
        """
        player_idx = action.player_idx
        character_idx = action.character_idx
        table = self.player_tables[player_idx]
        logging.info(
            f"Choose character action, player {player_idx}, "
            f"character {character_idx}, "
            f"name {table.characters[character_idx].name}"
        )
        original_character_idx = table.active_character_idx
        table.active_character_idx = character_idx
        # after choose character, add plunging mark
        table.plunge_satisfied = True
        event_arg = ChooseCharacterEventArguments(
            action=action, original_character_idx=original_character_idx
        )
        return [event_arg]

    def _action_create_dice(
        self, action: CreateDiceAction
    ) -> List[CreateDiceEventArguments]:
        """
        Create dice.
        """
        dice: List[DieColor] = []
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        number = action.number
        color = action.color
        is_random = action.random
        is_different = action.different
        if self.config.recreate_mode:
            # in recreate mode, all dice created is OMNI
            is_random = False
            is_different = False
            color = DieColor.OMNI
        if is_random and is_different:
            self._set_match_state(MatchState.ERROR)  # pragma no cover
            raise ValueError("Dice cannot be both random and different.")
        candidates: List[DieColor] = [
            DieColor.CRYO,
            DieColor.PYRO,
            DieColor.HYDRO,
            DieColor.ELECTRO,
            DieColor.GEO,
            DieColor.DENDRO,
            DieColor.ANEMO,
        ]
        # generate dice based on color
        if is_random:
            candidates.append(DieColor.OMNI)  # random, can be omni
            for _ in range(number):
                selected_color = candidates[int(self._random() * len(candidates))]
                dice.append(selected_color)
        elif is_different:
            if number > len(candidates):
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise ValueError("Not enough dice colors.")
            self._random_shuffle(candidates)
            candidates = candidates[:number]
            for selected_color in candidates:
                dice.append(selected_color)
        else:
            if color is None:
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise ValueError("Dice color should be specified.")
            for _ in range(number):
                dice.append(color)
        # if there are more dice than the maximum, discard the rest
        max_obtainable_dice = self.config.max_dice_number - len(table.dice.colors)
        table.dice.colors += dice[:max_obtainable_dice]
        # sort dice by color
        table.sort_dice()
        logging.info(
            f"Create dice action, player {player_idx}, "
            f"number {len(dice)}, "
            f"dice colors {dice}, "
            f"obtain {len(dice[:max_obtainable_dice])}, "
            f"over maximum {len(dice[max_obtainable_dice:])}, "
            f"current dice on table {table.dice}"
        )
        return [
            CreateDiceEventArguments(
                action=action,
                colors_generated=dice[:max_obtainable_dice],
                colors_over_maximum=dice[max_obtainable_dice:],
            )
        ]

    def _action_remove_dice(
        self, action: RemoveDiceAction
    ) -> List[RemoveDiceEventArguments]:
        player_idx = action.player_idx
        dice_idxs = action.dice_idxs
        table = self.player_tables[player_idx]
        removed_dice: List[DieColor] = []
        dice_idxs.sort(reverse=True)  # reverse order to avoid index error
        for idx in dice_idxs:
            removed_dice.append(table.dice.colors.pop(idx))
        # sort dice by color
        table.sort_dice()
        logging.info(
            f"Remove dice action, player {player_idx}, "
            f"number {len(dice_idxs)}, "
            f"dice colors {removed_dice.reverse()}, "
            f"current dice on table {table.dice}"
        )
        return [RemoveDiceEventArguments(action=action, colors_removed=removed_dice)]

    def _action_declare_round_end(
        self, action: DeclareRoundEndAction
    ) -> List[DeclareRoundEndEventArguments]:
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        logging.info(f"Declare round end action, player {player_idx}.")
        table.has_round_ended = True
        return [DeclareRoundEndEventArguments(action=action)]

    def _action_action_end(
        self, action: ActionEndAction
    ) -> List[ActionEndEventArguments]:
        player_idx = self.current_player
        combat_action_value = CombatActionValue(
            position=action.position,
            action_label=action.action_label,
            do_combat_action=action.do_combat_action,
        )
        self._modify_value(value=combat_action_value, mode="REAL")
        if action.do_combat_action and (
            (
                combat_action_value.action_label
                & (PlayerActionLabels.END.value | PlayerActionLabels.SKILL.value)
            )
            != 0
        ):
            # did any combat action that is not switch, remove plunging mark
            self.player_tables[player_idx].plunge_satisfied = False
        if not combat_action_value.do_combat_action:
            if action.do_combat_action:
                logging.info(
                    f"player {player_idx} did a combat action, but is "
                    f"modified as a quick action. current player "
                    f"is {self.current_player}."
                )
            else:
                logging.info(
                    f"player {player_idx} did a quick action, current player "
                    f"is {self.current_player}."
                )
            return [ActionEndEventArguments(action=action, do_combat_action=False)]
        if (
            self.player_tables[1 - player_idx].has_round_ended
            and not self.player_tables[player_idx].has_round_ended
        ):
            # the other player has declared round end and current player not,
            # do not change current player.
            pass
        else:
            # change current player. If no player has declared round end,
            # the current player will be changed to the other player.
            # Otherwise, two players all declared round end, the other player
            # goes first in the next round.
            self.current_player = 1 - player_idx
        logging.info(
            f"player {player_idx} did a combat action, current player "
            f"is {self.current_player}."
        )
        return [ActionEndEventArguments(action=action, do_combat_action=True)]

    def _action_switch_character(
        self, action: SwitchCharacterAction
    ) -> List[SwitchCharacterEventArguments]:
        """
        This action triggers by player manually declare character switch
        or by using skills or by overloaded. Be care of differences between
        choose_character when implementing event triggers.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        current_active_idx = table.active_character_idx
        current_active_name = table.characters[current_active_idx].name
        character_idx = action.character_idx
        character_name = table.characters[character_idx].name
        if table.characters[character_idx].is_defeated:
            self._set_match_state(MatchState.ERROR)  # pragma: no cover
            raise AssertionError(
                f"Cannot switch to defeated character {character_name}."
            )
        if table.active_character_idx == character_idx:
            self._set_match_state(MatchState.ERROR)  # pragma: no cover
            raise AssertionError(
                f"Cannot switch to the active character {character_name}."
            )
        logging.info(
            f"player {player_idx} "
            f"from character {current_active_name}:{current_active_idx} "
            f"switched to character {character_name}:{character_idx}."
        )
        table.active_character_idx = character_idx
        # after character switch, add plunging mark
        table.plunge_satisfied = True
        return [
            SwitchCharacterEventArguments(
                action=action,
                last_active_character_idx=current_active_idx,
            )
        ]

    def _action_make_damage(
        self, action: MakeDamageAction
    ) -> List[
        ReceiveDamageEventArguments
        | MakeDamageEventArguments
        | AfterMakeDamageEventArguments
        | SwitchCharacterEventArguments
        | CreateObjectEventArguments
    ]:
        """
        Make damage action. It contains make damage, heal and element
        application. It will return two types of events:
        1. MakeDamageEventArguments: All damage information dealt by this
            action.
        2. SwitchCharacterEventArguments: If this damage action contains
            character change, i.e. overloaded,
            a SwitchCharacterEventArguments will be generated.
        3. CreateObjectEventArguments: If this damage action contains create
            object, i.e. dendro reactions, a CreateObjectEventArguments
            will be generated.
        """
        damage_lists = action.damage_value_list[:]
        switch_character: List[int] = [-1, -1]
        create_objects: List[CreateObjectAction] = []
        assert self.event_handlers[0].name == "System"
        # version used in side effect generation
        version: str = self.event_handlers[0].version
        events: List[
            ReceiveDamageEventArguments
            | MakeDamageEventArguments
            | AfterMakeDamageEventArguments
            | SwitchCharacterEventArguments
            | CreateObjectEventArguments
        ] = []
        infos: List[ReceiveDamageEventArguments] = []
        while len(damage_lists) > 0:
            damage = damage_lists.pop(0)
            damage_original = damage.copy()
            assert (
                damage.target_position.area == ObjectPositionType.CHARACTER
            ), "Damage target position should be character."
            table = self.player_tables[damage.target_position.player_idx]
            character = table.characters[damage.target_position.character_idx]
            assert (
                damage.target_position.id == character.id
            ), "Damage target position should be character, id not match. "
            assert character.is_alive, "Damage target character should be alive."
            self._modify_value(damage, "REAL")
            damage_element_type = DAMAGE_TYPE_TO_ELEMENT[damage.damage_elemental_type]
            target_element_application = character.element_application
            [
                elemental_reaction,
                reacted_elements,
                applied_elements,
            ] = check_elemental_reaction(
                damage_element_type, target_element_application
            )
            if (
                elemental_reaction is ElementalReactionType.OVERLOADED
                and damage.target_position.character_idx == table.active_character_idx
            ):
                # overloaded to next character
                player_idx = damage.target_position.player_idx
                assert switch_character[player_idx] == -1, (
                    "When overloaded to switch character, which already "
                    "contain character switch rule."
                )
                nci = table.next_character_idx()
                if nci is not None:
                    switch_character[player_idx] = nci
            # apply elemental reaction, update damage and append new damages
            damage, new_damages, new_object = apply_elemental_reaction(
                table.characters,
                table.active_character_idx,
                damage,
                elemental_reaction,
                reacted_elements,
                version,
            )
            damage_lists += new_damages
            if new_object is not None:
                create_objects.append(new_object)
            # apply 3-step damage modification
            self._modify_value(damage, "REAL")
            damage = DamageMultiplyValue.from_increase_value(damage)
            self._modify_value(damage, "REAL")
            damage = DamageDecreaseValue.from_multiply_value(damage)
            self._modify_value(damage, "REAL")
            # apply final damage and applied elements
            hp_before = character.hp
            character.hp -= damage.damage
            if character.hp < 0:
                character.hp = 0
            if character.hp > character.max_hp:
                character.hp = character.max_hp
            character.element_application = applied_elements
            infos.append(
                ReceiveDamageEventArguments(
                    action=action,
                    original_damage=damage_original,
                    final_damage=damage,
                    hp_before=hp_before,
                    hp_after=character.hp,
                    elemental_reaction=elemental_reaction,
                    reacted_elements=reacted_elements,
                )
            )
        for info in infos:
            if info.final_damage.damage_type == DamageType.ELEMENT_APPLICATION:
                # ignore element application
                continue
            target = info.final_damage.target_position
            pidx = target.player_idx
            cidx = target.character_idx
            if pidx not in self.action_info:
                self.action_info[pidx] = {}
            if cidx not in self.action_info[pidx]:
                self.action_info[pidx][cidx] = []
            damage_type = info.final_damage.damage_elemental_type
            damage = info.final_damage.damage
            if damage_type == DamageElementalType.HEAL:
                damage = -damage
            self.action_info[pidx][cidx].append(
                {
                    "type": damage_type,
                    "damage": damage,
                }
            )
        make_damage_event = MakeDamageEventArguments(
            action=action,
            damages=infos,
        )
        events.append(make_damage_event)
        events += infos
        events.append(
            AfterMakeDamageEventArguments.from_make_damage_event_arguments(
                make_damage_event
            )
        )
        for table, sc in zip(self.player_tables, switch_character):
            if sc != -1 and sc != table.active_character_idx:
                # character switch
                sw_action = SwitchCharacterAction(
                    player_idx=table.player_idx,
                    character_idx=sc,
                )
                sw_events = self._action_switch_character(sw_action)
                events += sw_events
        for co_action in create_objects:
            co_events = self._action_create_object(co_action)
            events += co_events
        return events

    def _action_charge(self, action: ChargeAction) -> List[ChargeEventArguments]:
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        character = table.characters[action.character_idx]
        assert character.is_alive, "Cannot charge a defeated character."
        logging.info(
            f"player {player_idx} "
            f"character {character.name}:{table.active_character_idx} "
            f"charged {action.charge}."
        )
        old_charge = character.charge
        character.charge += action.charge
        if character.charge > character.max_charge:
            character.charge = character.max_charge
        # charge should not be negative, unless in prediction mode
        if self._prediction_mode:
            if character.charge < 0:
                character.charge = 0
        else:
            assert character.charge >= 0
        return [
            ChargeEventArguments(
                action=action,
                charge_before=old_charge,
                charge_after=character.charge,
            )
        ]

    def _action_character_defeated(
        self, action: CharacterDefeatedAction
    ) -> List[CharacterDefeatedEventArguments | RemoveObjectEventArguments]:
        """
        Character defeated action, all equipment and status are removed,
        and is marked as defeated. Currently not support PVE character
        disappear features. Event arguments returned contains
        CharacterDefeatedEventArguments and RemoveObjectEventArguments.
        """
        ret: List[CharacterDefeatedEventArguments | RemoveObjectEventArguments] = []
        player_idx = action.player_idx
        character_idx = action.character_idx
        table = self.player_tables[player_idx]
        character = table.characters[character_idx]
        assert character.is_defeated, "Should marked as defeated character."
        logging.info(
            f"player {player_idx} "
            f"character {character.name}:{character_idx} "
            f"defeated."
        )
        removed_objects = character.attaches
        for obj in removed_objects:
            ret.append(
                RemoveObjectEventArguments(
                    action=RemoveObjectAction(
                        object_position=obj.position,
                    ),
                    object_name=obj.name,
                    object_type=obj.type,
                )
            )
            self.trashbin.append(obj)
        character.attaches = []
        character.element_application = []
        character.is_alive = False
        character.charge = 0
        need_switch = False
        if table.active_character_idx == character_idx:
            table.active_character_idx = -1  # reset active character
            need_switch = True
        ret.append(
            CharacterDefeatedEventArguments(
                action=action,
                need_switch=need_switch,
            )
        )
        return ret

    def _action_character_revive(
        self, action: CharacterReviveAction
    ) -> List[CharacterReviveEventArguments]:
        """
        Character revive action. A defeated character is revived.
        """
        player_idx = action.player_idx
        character_idx = action.character_idx
        table = self.player_tables[player_idx]
        character = table.characters[character_idx]
        assert character.is_defeated, "Cannot revive a living character."
        logging.info(
            f"player {player_idx} "
            f"character {character.name}:{character_idx} "
            f"revived with {action.revive_hp} HP."
        )
        character.is_alive = True
        character.hp = action.revive_hp
        return [
            CharacterReviveEventArguments(
                action=action,
            )
        ]

    def _action_create_object(
        self, action: CreateObjectAction
    ) -> List[CreateObjectEventArguments]:
        """
        Action for creating objects, e.g. status, summons, supports.
        Note some objects are not created but moved, e.g. equipment and
        supports, for these objects, do not use this action.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # character_idx = action.object_position.character_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_class = TeamStatusBase
            target_list = renew_target_list = table.team_status
            target_name = "team status"
        elif action.object_position.area == ObjectPositionType.CHARACTER_STATUS:
            target_class = CharacterStatusBase
            target_list = table.characters[
                action.object_position.character_idx
            ].attaches
            renew_target_list = table.characters[
                action.object_position.character_idx
            ].status
            character = table.characters[action.object_position.character_idx]
            if character.is_defeated:  # pragma: no cover
                logging.warning(
                    "Trying to create status for defeated character "
                    f"{action.object_position.player_idx}:"
                    f"{action.object_position.character_idx}:"
                    f"{character.name}. Is it be defeated before creating "
                    "or a bug?"
                )
                return []
            target_name = "character status"
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_class = SummonBase
            target_list = renew_target_list = table.summons
            target_name = "summon"
        elif action.object_position.area == ObjectPositionType.HAND:
            if len(table.hands) >= self.config.max_hand_size:
                logging.warning(
                    f"Player {player_idx} "
                    f"tried to create new hand {action.object_name}, "
                    "but hand size is already maximum."
                )
                return [
                    CreateObjectEventArguments(
                        action=action,
                        create_result="FAIL",
                    )
                ]
            target_class = CardBase
            target_list = renew_target_list = table.hands
            target_name = "hand"
        elif action.object_position.area == ObjectPositionType.SYSTEM:
            target_class = SystemEventHandlerBase
            target_list = renew_target_list = self.event_handlers
            target_name = "system event handler"
        else:
            raise NotImplementedError(
                f"Create object action for area {action.object_position.area} "
                "is not implemented."
            )
        args = action.object_arguments.copy()
        args["name"] = action.object_name
        args["position"] = action.object_position
        target_object = get_instance(target_class, args)
        if target_name != "hand":
            # if not create hand, not allow to create same name object
            for csnum, current_object in enumerate(renew_target_list):
                if current_object.name == target_object.name:
                    # have same name object, only update status usage
                    current_object.renew(target_object)  # type: ignore
                    logging.info(
                        f"player {player_idx} "
                        f"renew {target_name} {action.object_name}."
                    )
                    return [
                        CreateObjectEventArguments(
                            action=action,
                            create_result="RENEW",
                        )
                    ]
        if (
            target_name == "summon"
            and len(target_list) >= self.config.max_summon_number
        ):
            # summon number reaches maximum
            logging.warning(
                f"player {player_idx} "
                f"tried to create new {target_name} {action.object_name}, "
                f"but summon number reaches maximum "
                f"{self.config.max_summon_number}, and will not create "
                "the summon."
            )
            return []
        logging.info(
            f"player {player_idx} " f"created new {target_name} {action.object_name}."
        )
        target_list.append(target_object)  # type: ignore
        return [
            CreateObjectEventArguments(
                action=action,
                create_result="NEW",
            )
        ]

    def _action_create_random_object(
        self, action: CreateRandomObjectAction
    ) -> List[CreateObjectEventArguments]:
        """
        Action for creating random objects, e.g. Abyss Summoning and elemental skills
        of Rhodeia. If in recreate mode, will create objects based on hints.
        TODO now it will create multiple `CreateObjectEventArguments` and no specified
        event arguments for this action directly. If it is needed, may add it after.
        """
        assert action.number <= len(action.object_names), (
            "Number of objects to create should be less than or equal to "
            "number of object names."
        )
        events: List[CreateObjectEventArguments] = []
        while action.number > 0:
            if self.config.recreate_mode:
                name = self.config.random_object_information.pop(0)
                assert name in action.object_names, (
                    f"In recreate mode, next random object name ({name}) should "
                    f"be in object names ({' '.join(action.object_names)})."
                )
                idx = action.object_names.index(name)
            else:
                idx = int(self._random() * len(action.object_names))
            coa, action = action.select_by_idx(idx)
            events += self._action_create_object(coa)
        return events

    def _action_remove_object(
        self, action: RemoveObjectAction
    ) -> List[RemoveObjectEventArguments]:
        """
        Action for removing objects, e.g. status, summons, supports.
        It supports removing equipment and supports.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # character_idx = action.object_position.character_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_list = table.team_status
            target_name = "team status"
        elif action.object_position.area == ObjectPositionType.CHARACTER_STATUS:
            target_list = table.characters[
                action.object_position.character_idx
            ].attaches
            target_name = "character status"
            assert table.characters[
                action.object_position.character_idx
            ].is_alive, "Cannot remove status for defeated character now."
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_list = table.summons
            target_name = "summon"
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            target_list = table.supports
            target_name = "support"
        elif action.object_position.area == ObjectPositionType.CHARACTER:
            # remove artifact, weapon or talent
            character = table.characters[action.object_position.character_idx]
            assert (
                character.is_alive
            ), "Cannot remove equips for defeated character now."
            removed_equip = None
            if (
                character.weapon is not None
                and character.weapon.id == action.object_position.id
            ):
                removed_equip = character.weapon
                target_name = "weapon"
                target_type = ObjectType.WEAPON
            elif (
                character.artifact is not None
                and character.artifact.id == action.object_position.id
            ):
                removed_equip = character.artifact
                target_name = "artifact"
                target_type = ObjectType.ARTIFACT
            elif (
                character.talent is not None
                and character.talent.id == action.object_position.id
            ):
                removed_equip = character.talent
                target_name = "talent"
                target_type = ObjectType.TALENT
            else:
                raise AssertionError(
                    f"player {player_idx} tried to remove non-exist equipment "
                    f"from character {character.name} with id "
                    f"{action.object_position.id}."
                )
            removed_equip = character.remove_equip(target_type)
            self.trashbin.append(removed_equip)  # type: ignore
            return [
                RemoveObjectEventArguments(
                    action=action,
                    object_name=removed_equip.name,
                    object_type=removed_equip.type,
                )
            ]
        else:
            raise NotImplementedError(
                f"Remove object action for area "
                f"{action.object_position.area} is not implemented."
            )
        for csnum, current_object in enumerate(target_list):
            if current_object.id == action.object_position.id:
                # have same status, only update status usage
                removed_object = target_list.pop(csnum)
                logging.info(
                    f"player {player_idx} "
                    f"removed {target_name} {current_object.name}."
                )
                self.trashbin.append(removed_object)  # type: ignore
                return [
                    RemoveObjectEventArguments(
                        action=action,
                        object_name=current_object.name,
                        object_type=current_object.type,
                    )
                ]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f"player {player_idx} "
            f"tried to remove non-exist {target_name} with id "
            f"{action.object_position.id}."
        )

    def _action_change_object_usage(
        self, action: ChangeObjectUsageAction
    ) -> List[ChangeObjectUsageEventArguments]:
        """
        Action for changing object usage, e.g. status, summons, supports.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # character_idx = action.object_position.character_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_list = table.team_status
            target_name = "team status"
        elif action.object_position.area == ObjectPositionType.CHARACTER_STATUS:
            target_list = table.characters[action.object_position.character_idx].status
            target_name = "character status"
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            target_list = table.supports
            target_name = "support"
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_list = table.summons
            target_name = "summon"
        else:
            raise NotImplementedError(
                f"Change object usage action for area "
                f"{action.object_position.area} is not implemented."
            )
        for csnum, current_object in enumerate(target_list):
            if current_object.id == action.object_position.id:
                # have same status, only update status usage
                old_usage = current_object.usage
                new_usage = action.change_usage
                new_usage += old_usage
                new_usage = min(max(new_usage, action.min_usage), action.max_usage)
                current_object.usage = new_usage
                logging.info(
                    f"player {player_idx} "
                    f"changed {target_name} {current_object.name} "
                    f"usage to {new_usage}."
                )
                return [
                    ChangeObjectUsageEventArguments(
                        action=action,
                        object_name=current_object.name,
                        usage_before=old_usage,
                        usage_after=new_usage,
                    )
                ]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f"player {player_idx} "
            f"tried to change non-exist {target_list} with id "
            f"{action.object_position.id}."
        )
        return []

    def _action_move_object(
        self, action: MoveObjectAction
    ) -> List[MoveObjectEventArguments]:
        """
        Action for moving objects, e.g. equipment, supports.
        """
        player_idx = action.object_position.player_idx
        character_idx = action.object_position.character_idx
        table = self.player_tables[player_idx]
        assert action.object_position.id == action.target_position.id, (
            "Move object action should have same object id in both "
            "object position and target position."
        )
        # character_idx = action.object_position.character_id
        if action.object_position.area == ObjectPositionType.HAND:
            assert table.using_hand is not None
            current_list = [table.using_hand]
            table.using_hand = None
            current_name = "hand"
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            current_list = table.supports
            current_name = "support"
        elif action.object_position.area == ObjectPositionType.CHARACTER:
            # move equipment
            character = table.characters[character_idx]
            weapon = character.weapon
            artifact = character.artifact
            talent = character.talent
            if weapon is not None and weapon.id == action.object_position.id:
                current_list = [character.remove_equip(ObjectType.WEAPON)]
                current_name = "weapon"
            elif artifact is not None and artifact.id == action.object_position.id:
                current_list = [character.remove_equip(ObjectType.ARTIFACT)]
                current_name = "artifact"
            elif talent is not None and talent.id == action.object_position.id:
                raise NotImplementedError("Talent cannot be moved now.")
                current_list = [character.remove_equip(ObjectType.TALENT)]
                current_name = "talent"
            else:
                raise AssertionError(
                    f"player {player_idx} tried to move non-exist equipment "
                    f"from character {character_idx} with id "
                    f"{action.object_position.id}."
                )
        else:
            raise NotImplementedError(
                f"Move object action from area "
                f"{action.object_position.area} is not implemented."
            )
        table = self.player_tables[action.target_position.player_idx]
        for csnum, current_object in enumerate(current_list):
            if current_object.id == action.object_position.id:
                if action.target_position.area == ObjectPositionType.HAND:
                    target_list = table.hands
                    target_name = "hand"
                elif action.target_position.area == ObjectPositionType.SUPPORT:
                    target_list = table.supports
                    assert current_object.type == ObjectType.SUPPORT
                    assert len(target_list) < self.config.max_support_number
                    target_name = "support"
                elif action.target_position.area == ObjectPositionType.CHARACTER:
                    # quip equipment
                    assert (
                        action.object_position.player_idx
                        == action.target_position.player_idx
                    )
                    character = table.characters[action.target_position.character_idx]
                    assert character.is_alive, "Cannot equip to defeated character now."
                    current_list.pop(csnum)
                    current_object.position = action.target_position
                    if current_object.type == ObjectType.ARTIFACT:
                        assert character.artifact is None
                        target_name = "artifact"
                    elif current_object.type == ObjectType.TALENT:
                        assert character.talent is None
                        target_name = "talent"
                    elif current_object.type == ObjectType.WEAPON:
                        assert character.weapon is None
                        target_name = "weapon"
                    else:
                        raise NotImplementedError(
                            f"Move object action as eqipment with type "
                            f"{current_object.type} is not implemented."
                        )
                    character.attaches.append(current_object)  # type: ignore
                    logging.info(
                        f"player {player_idx} "
                        f"moved {current_name} {current_object.name} "
                        f"to character {action.target_position.character_idx}"
                        f":{target_name}."
                    )
                    return [
                        MoveObjectEventArguments(
                            action=action,
                            object_name=current_object.name,
                        )
                    ]
                else:
                    raise NotImplementedError(
                        f"Move object action to area "
                        f"{action.target_position.area} is not implemented."
                    )
                current_list.pop(csnum)
                current_object.position = action.target_position
                target_list.append(current_object)  # type: ignore
                logging.info(
                    f"player {player_idx} "
                    f"moved {current_name} {current_object.name} "
                    f"to {target_name}."
                )
                return [
                    MoveObjectEventArguments(
                        action=action,
                        object_name=current_object.name,
                    )
                ]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f"player {player_idx} "
            f"tried to move non-exist {current_name} with id "
            f"{action.object_position.id}."
        )
        return []

    def _action_consume_arcane_legend(
        self, action: ConsumeArcaneLegendAction
    ) -> List[ConsumeArcaneLegendEventArguments]:
        """
        Action for consuming arcane legend.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        assert table.arcane_legend, f"Arcane legend of player {player_idx} is consumed"
        table.arcane_legend = False
        logging.info(f"player {player_idx} consumed arcane legend.")
        return [
            ConsumeArcaneLegendEventArguments(
                action=action,
            )
        ]

    """
    Action functions that only used to trigger specific event
    """

    def _action_use_skill(self, action: UseSkillAction) -> List[UseSkillEventArguments]:
        player_idx = action.skill_position.player_idx
        table = self.player_tables[player_idx]
        character = table.characters[table.active_character_idx]
        skill = character.get_object(action.skill_position)
        assert skill is not None and skill.type == ObjectType.SKILL
        logging.info(
            f"player {player_idx} "
            f"character {character.name}:{table.active_character_idx} "
            f"use skill {skill.name}."  # type: ignore
        )
        return [
            UseSkillEventArguments(
                action=action,
            )
        ]

    def _action_use_card(self, action: UseCardAction) -> List[UseCardEventArguments]:
        assert (
            action.card_position.area == ObjectPositionType.HAND
        ), "Card should be used from hand."
        table = self.player_tables[action.card_position.player_idx]
        hands = table.hands
        for idx, c in enumerate(hands):
            if c.id == action.card_position.id:
                table.using_hand = c
                table.hands.pop(idx)
                break
        else:  # pragma: no cover
            self._set_match_state(MatchState.ERROR)
            raise AssertionError(
                f"player {action.card_position.player_idx} "
                f"tried to use non-exist card with id "
                f"{action.card_position.id}."
            )
        card = table.using_hand

        # check if use success
        use_card_value = UseCardValue(position=card.position, card=card)
        self._modify_value(use_card_value, "REAL")

        info_str = f"player {action.card_position.player_idx} use card {card.name}."
        if not use_card_value.use_card:
            info_str += " But use card failed!"
        logging.info(info_str)

        return [
            UseCardEventArguments(
                action=action,
                card_name=card.name,
                card_cost=card.cost,
                use_card_success=use_card_value.use_card,
            )
        ]

    def _action_skill_end(self, action: SkillEndAction) -> List[SkillEndEventArguments]:
        player_idx = action.position.player_idx
        character_idx = action.position.character_idx
        table = self.player_tables[player_idx]
        character = table.characters[character_idx]
        logging.info(
            f"player {player_idx} "
            f"character {character.name}:{character_idx} "
            f"skill ended."
        )
        return [
            SkillEndEventArguments(
                action=action,
            )
        ]

    """
    Action functions that generate requests. Should not trigger event, i.e.
    return empty list.
    """

    def _action_generate_choose_character_request(
        self, action: GenerateChooseCharacterRequestAction
    ) -> List[EventArgumentsBase]:
        self._request_choose_character(action.player_idx)
        if self.config.history_level > 0:
            self._save_history()
        return []

    def _action_generate_reroll_dice_request(
        self, action: GenerateRerollDiceRequestAction
    ) -> List[EventArgumentsBase]:
        self._request_reroll_dice(action.player_idx, action.reroll_times)
        if self.config.history_level > 0:
            self._save_history()
        return []

    def _action_generate_switch_card_request(
        self, action: GenerateSwitchCardRequestAction
    ) -> List[EventArgumentsBase]:
        self._request_switch_card(action.player_idx)
        if self.config.history_level > 0:
            self._save_history()
        return []

    """
    Action functions the changes game state. Some skill will occupy multiple
    action phase, so use this action to skip player action generation.
    These actions should not trigger event, i.e. return empty list.
    """

    def _action_skip_player_action(
        self, action: SkipPlayerActionAction
    ) -> List[ActionEndEventArguments]:
        """
        In this action, match state is changed to PLAYER_ACTION_REQUEST, so
        no requests are generated to current player, and it will immediately end
        the action phase.
        """
        if self.state != MatchState.PLAYER_ACTION_START:
            raise AssertionError(
                f"Cannot skip player action when match state is " f"{self.state}."
            )
        self._set_match_state(MatchState.PLAYER_ACTION_REQUEST)
        logging.info(f"player {self.current_player} skipped player action.")
        return self._action_action_end(action.get_action_end_action())
