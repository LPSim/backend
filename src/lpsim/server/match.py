import os
import logging

import numpy as np
from typing import Literal, List, Any, Dict, Tuple
from enum import Enum
from pydantic import PrivateAttr, validator
import dictdiffer

from .summon.base import SummonBase

from .status.team_status.base import TeamStatusBase

from .status.charactor_status.base import CharactorStatusBase

from ..utils import BaseModel, get_instance
from .deck import Deck
from .player_table import PlayerTable
from .action import (
    ActionBase, ActionTypes, Actions,
    DrawCardAction,
    RestoreCardAction,
    RemoveCardAction,
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
    DeclareRoundEndAction,
    ActionEndAction, SkipPlayerActionAction,
    SwitchCharactorAction,
    MakeDamageAction,
    ChargeAction, UseCardAction,
    UseSkillAction,
    # UseCardAction,
    SkillEndAction,
    CreateObjectAction,
    RemoveObjectAction,
    ChangeObjectUsageAction,
    MoveObjectAction,
    CharactorDefeatedAction,
    GenerateChooseCharactorRequestAction,
    GenerateRerollDiceRequestAction,
    CharactorReviveAction,
    ConsumeArcaneLegendAction,
    GenerateSwitchCardRequestAction,
)
from .interaction import (
    Requests, Responses, 
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    ElementalTuningRequest, ElementalTuningResponse,
    DeclareRoundEndRequest, DeclareRoundEndResponse,
    UseSkillRequest, UseSkillResponse,
    UseCardRequest, UseCardResponse,
)
from .consts import (
    CostLabels, DamageElementalType, DamageType, DieColor, 
    ELEMENT_TO_DIE_COLOR, DAMAGE_TYPE_TO_ELEMENT, ElementalReactionType,
    ObjectPositionType, ObjectType, PlayerActionLabels, SkillType,
)
from .event import (
    CharactorReviveEventArguments,
    PlayerActionStartEventArguments,
    ConsumeArcaneLegendEventArguments,
    EventArguments,
    EventArgumentsBase,
    DrawCardEventArguments,
    EventFrame,
    GameStartEventArguments, 
    RestoreCardEventArguments, 
    RemoveCardEventArguments,
    ChooseCharactorEventArguments,
    CreateDiceEventArguments,
    RemoveDiceEventArguments,
    RoundPrepareEventArguments,
    DeclareRoundEndEventArguments,
    ActionEndEventArguments,
    SwitchCharactorEventArguments,
    ChargeEventArguments,
    SkillEndEventArguments,
    ReceiveDamageEventArguments,
    MakeDamageEventArguments,
    AfterMakeDamageEventArguments,
    CharactorDefeatedEventArguments,
    RoundEndEventArguments,
    CreateObjectEventArguments,
    RemoveObjectEventArguments,
    ChangeObjectUsageEventArguments,
    MoveObjectEventArguments,
    UseCardEventArguments,
    UseSkillEventArguments,
)
from .object_base import CardBase, ObjectBase
from .modifiable_values import (
    CombatActionValue,
    ModifiableValueBase,
    InitialDiceColorValue,
    ModifiableValueTypes, RerollValue, CostValue,
    DamageMultiplyValue, DamageDecreaseValue,
    UseCardValue,
)
from .struct import (
    ObjectPosition, Cost
)
from .elemental_reaction import (
    check_elemental_reaction,
    apply_elemental_reaction,
)
from .event_handler import SystemEventHandlerBase, SystemEventHandler


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
        STARTING_CHOOSE_CHARACTOR (str): Waiting for players to choose
            charactors.
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
    INVALID = 'INVALID'
    ERROR = 'ERROR'
    WAITING = 'WAITING'

    STARTING = 'STARTING'
    STARTING_CARD_SWITCH = 'STARTING_CARD_SWITCH'
    STARTING_CHOOSE_CHARACTOR = 'STARTING_CHOOSE_CHARACTOR'

    GAME_START = 'GAME_START'

    ROUND_START = 'ROUND_START'
    ROUND_ROLL_DICE = 'ROUND_ROLL_DICE'
    ROUND_PREPARING = 'ROUND_PREPARING'

    PLAYER_ACTION_START = 'PLAYER_ACTION_START'
    PLAYER_ACTION_REQUEST = 'PLAYER_ACTION_REQUEST'

    ROUND_ENDING = 'ROUND_ENDING'
    ROUND_ENDED = 'ROUND_ENDED'

    ENDED = 'ENDED'

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
    charactor_number: int | None = 3
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
    NOTE: It is slow to save history, normally should not use it in
    non-frontend tasks.
    """
    history_level: int = 0

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
    For random effects, e.g. Abyss Sommon, or Rhodeia's skill, they will read
    orders from random_object_information. The key is defined by the skill,
    usually the skill name, refer to source code to check. The value is a list
    of created object names, it will check whether the first name of current 
    list is valid, remove the name and generate corresponding object. 

    TODO: As all dice are omni, Liben and Vanarana may have non-reproducible
    results. Need to fix it.
    """
    recreate_mode: bool = False
    random_object_information: Dict[str, List[str]] = {}

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
            or (self.max_same_card_number is not None
                and self.max_same_card_number < 0)
            or (self.charactor_number is not None
                and self.charactor_number < 0)
            or self.max_round_number <= 0
            or self.max_hand_size < 0
            or self.max_dice_number < 0
            or self.max_summon_number < 0
            or self.max_support_number < 0
        ):
            return False
        if self.initial_hand_size > self.max_hand_size:
            logging.error('initial hand size should not be greater than '
                          'max hand size')
            return False
        if self.initial_card_draw > self.max_hand_size:
            logging.error('initial card draw should not be greater than '
                          'max hand size')
            return False

        if (
            self.card_number is not None
            and self.initial_card_draw > self.card_number
        ):
            logging.error('initial card draw should not be greater than '
                          'card number')
            return False
        if self.initial_dice_number > self.max_dice_number:
            logging.error('initial dice number should not be greater than '
                          'max dice number')
            return False
        if self.history_level < 0:
            logging.error('history level should not be less than 0')
            return False
        return True


class Match(BaseModel):
    """
    """

    name: Literal['Match'] = 'Match'

    version: Literal['0.0.1', '0.0.2', '0.0.3', '0.0.4'] = '0.0.4'

    config: MatchConfig = MatchConfig()

    '''
    history logger and last action recorder. 
    history_diff[i] records the difference between _history[i - 1] and 
    _history[i], which is used in data transmission.
    action_info is used to record information that generated during the action,
    e.g. for MakeDamageAction, it will record the detailed damage information, 
    which has applied elemental reaction and value modification.
    '''
    _history: List['Match'] = PrivateAttr(default_factory = list)
    _history_diff: List = PrivateAttr(default_factory = list)
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
    _random_state: np.random.RandomState = PrivateAttr(np.random.RandomState())

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
    event_frames: List[EventFrame] = []
    requests: List[Requests] = []
    winner: int = -1

    # debug params
    _debug_save_appeared_object_names: bool = PrivateAttr(False)
    _debug_appeared_object_names_versions: Any = PrivateAttr({})
    _debug_save_file_name: str = PrivateAttr('')

    # In event chain, all removed objects will firstly move to the trashbin. 
    # If some object explicitly claims that some event handlers will work in
    # trashbin, these events will be triggered in trashbin. After all event
    # chain cleared, all objects in trashbin will be removed.
    trashbin: List[
        CharactorStatusBase | TeamStatusBase | CardBase | SummonBase
    ] = []

    @validator('event_handlers', each_item = True, pre = True)
    def parse_event_handlers(cls, v):
        return get_instance(SystemEventHandlerBase, v)

    # @validator('requests', each_item = True, pre = True)
    # def parse_requests(cls, v):
    #     return get_instance(Requests, v)

    @validator('trashbin', each_item = True, pre = True)
    def parse_trashbin(cls, v):
        return get_instance(
            CharactorStatusBase | TeamStatusBase | CardBase | SummonBase, v
        )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if len(self.player_tables) == 0:
            self.player_tables.append(PlayerTable(
                version = self.version,
                player_idx = 0,
            ))
            self.player_tables.append(PlayerTable(
                version = self.version,
                player_idx = 1,
            ))
        self._init_random_state()

    def copy(self, *argv, **kwargs) -> 'Match':
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
            random_state = self.random_state[:]
            random_state[1] = np.array(random_state[1], dtype = 'uint32')
            self._random_state.set_state(random_state)  # type: ignore
        else:
            # random state not set, re-new self._random_state to avoid
            # affecting other matches.
            self._random_state = np.random.RandomState()
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
        copy = self.copy(deep = True)
        self._history += hist
        self._history_diff += hist_diff
        self._history.append(copy)
        if len(self._history) == 1:
            self._history_diff.append(None)
        else:
            self._history_diff.append(list(
                dictdiffer.diff(self._history[-2].dict(), 
                                self._history[-1].dict())
            ))
            # remove prev values of 'remove' in diff
            diff = self._history_diff[-1]
            for d in diff:
                if d[0] == 'remove':
                    for i in range(len(d[2])):
                        d[2][i] = (d[2][i][0], None)

    def _debug_save_appeared_object_names_to_file(self):  # pragma: no cover
        # save appeared object names and descs
        if self._debug_save_file_name == '':
            import time
            self._debug_save_file_name = str(time.time())
        for obj in self.get_object_list():
            name = obj.name  # type: ignore
            type = obj.type
            version = ''
            if hasattr(obj, 'version'):
                version = obj.version  # type: ignore
            desc = ''
            if hasattr(obj, 'desc'):
                desc = obj.desc  # type: ignore
            if type == ObjectType.SKILL:
                # record skill type and its corresponding charactor and 
                # charactor's version
                charactor = self.player_tables[
                    obj.position.player_idx].charactors[
                        obj.position.charactor_idx]
                skill_type = obj.skill_type  # type: ignore
                type = f'{type}_{charactor.name}_{skill_type}'
                version = charactor.version
            elif type == ObjectType.TALENT:
                # record its corresponding charactor
                type = f'{type}_{obj.charactor_name}'  # type: ignore
            if type not in self._debug_appeared_object_names_versions:
                self._debug_appeared_object_names_versions[type] = {}
            if name not in self._debug_appeared_object_names_versions[type]:
                self._debug_appeared_object_names_versions[type][name] = {}
            self._debug_appeared_object_names_versions[
                type][name][version] = desc
        import json
        target_folder = 'logs/obj_name_descs'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        open(f'{target_folder}/{self._debug_save_file_name}.txt', 'w').write(
            json.dumps(self._debug_appeared_object_names_versions, indent = 2)
        )

    def set_deck(self, decks: List[Deck]):
        """
        Set the deck of the match.
        """
        if self.state != MatchState.WAITING:
            raise ValueError('Match is not in waiting state.')
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
        res = [match.json() for match in self._history]
        if filename is not None:
            with open(filename, 'w') as f:
                f.write('\n'.join(res))
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
        self.random_state = list(self._random_state.get_state(
            legacy = True))  # type: ignore
        self.random_state[1] = self.random_state[1].tolist()

    def _random(self):
        """
        Return a random number ranges 0-1 based on random_state, and save new
        random state.
        """
        assert not self.config.recreate_mode, (
            'In recreate mode, random functions should not be called.'
        )
        ret = self._random_state.random()
        self._save_random_state()
        return ret

    def _random_shuffle(self, array: List):
        """
        Shuffle the array based on random_state.
        """
        assert not self.config.recreate_mode, (
            'In recreate mode, random functions should not be called.'
        )
        self._random_state.shuffle(array)
        self._save_random_state()

    def _set_match_state(self, new_state: MatchState):
        logging.info(f'Match state change from {self.state} to '
                     f'{new_state}.')
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
                'Match is not waiting for start. If it is running '
                'or ended, please re-generate a new match.'
            )
            logging.error(error_message)
            return False, error_message

        # make valid check
        if not self.config.check_config():
            error_message = 'Match config is not valid.'
            logging.error('Match config is not valid.')
            return False, error_message
        if len(self.player_tables) != 2:
            error_message = 'Only support 2 players now.'
            logging.error(error_message)
            return False, error_message
        for pnum, player_table in enumerate(self.player_tables):
            is_legal, info = player_table.player_deck_information.check_legal(
                card_number = self.config.card_number,
                max_same_card_number = self.config.max_same_card_number,
                charactor_number = self.config.charactor_number,
                check_restriction = self.config.check_deck_restriction,
            )
            if not is_legal:
                error_message = f'Player {pnum} deck is not legal. {info}'
                logging.error(error_message)
                return False, error_message

        self._set_match_state(MatchState.STARTING)

        # choose first player
        if self.config.random_first_player and not self.config.recreate_mode:
            self.current_player = int(self._random() > 0.5)
        else:
            self.current_player = self.config.player_go_first
        logging.info(f'Player {self.current_player} is the first player')

        # copy and randomize based on deck
        for pnum, player_table in enumerate(self.player_tables):
            # copy charactors
            for cnum, charactor in enumerate(
                    player_table.player_deck_information.charactors):
                charactor_copy = charactor.copy(deep = True)
                charactor_copy.position = ObjectPosition(
                    player_idx = pnum,
                    charactor_idx = cnum,
                    area = ObjectPositionType.CHARACTOR,
                    id = charactor_copy.id
                )
                charactor_copy.renew_id()
                player_table.charactors.append(charactor_copy)
            # copy cards
            if self.config.recreate_mode:
                # in recreate mode, do not shuffle cards, only copy to table
                # deck
                for card in player_table.player_deck_information.cards:
                    card_copy = card.copy(deep = True)
                    card_copy.position = ObjectPosition(
                        player_idx = pnum,
                        area = ObjectPositionType.DECK,
                        id = card_copy.id
                    )
                    card_copy.renew_id()
                    player_table.table_deck.append(card_copy)
            else:
                arcane_legend_cards = []
                for card in player_table.player_deck_information.cards:
                    card_copy = card.copy(deep = True)
                    card_copy.position = ObjectPosition(
                        player_idx = pnum,
                        area = ObjectPositionType.DECK,
                        id = card_copy.id
                    )
                    card_copy.renew_id()
                    if card_copy.type == ObjectType.ARCANE:
                        arcane_legend_cards.append(card_copy)
                    else:
                        player_table.table_deck.append(card_copy)
                if len(arcane_legend_cards):
                    # have arcane legend cards, they must in hand
                    if (
                        len(arcane_legend_cards) 
                        > self.config.initial_hand_size
                    ):
                        # shuffle arcane legend cards, and put over-maximum
                        # into table deck
                        self._random_shuffle(arcane_legend_cards)
                        player_table.table_deck += arcane_legend_cards[
                            self.config.initial_hand_size:]
                        arcane_legend_cards = arcane_legend_cards[
                            :self.config.initial_hand_size]
                # shuffle deck
                self._random_shuffle(player_table.table_deck)
                # prepend arcane legend cards
                player_table.table_deck = (
                    arcane_legend_cards + player_table.table_deck
                )
            # add draw initial cards action
            event_args = self._act(DrawCardAction(
                player_idx = pnum, 
                number = self.config.initial_hand_size,
                draw_if_filtered_not_enough = True,
            ))
            event_frame = self._stack_events(event_args)
            self.empty_frame_assertion(
                event_frame = event_frame,
                error_message = 'Initial draw card should not trigger objects.'
            )
        return True, None

    def empty_frame_assertion(
        self, event_frame: EventFrame, error_message: str
    ) -> None:
        while len(event_frame.events):
            self._trigger_event(event_frame)
            while len(event_frame.triggered_objects):
                position = event_frame.triggered_objects.pop(0)
                object = self.get_object(position)
                event_arg = event_frame.processing_event
                assert event_arg is not None
                handler_name = 'event_handler_' + event_arg.type.value
                func = getattr(object, handler_name)
                actions = func(event_frame.processing_event, self)
                if len(actions):
                    self._set_match_state(MatchState.ERROR)  # pragma no cover
                    raise AssertionError(error_message)

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
                    logging.error('Match has already ended.')
                    return False
            # check if it need response
            elif len(self.requests) != 0:
                logging.info('There are still requests not responded.')
                return False
            # check if action is needed
            elif len(self.event_frames) != 0:
                self._next_action()
            # all response and action are cleared, start state transition
            elif self.state == MatchState.STARTING:
                self._set_match_state(MatchState.STARTING_CARD_SWITCH)
                for player_idx in range(len(self.player_tables)):
                    self._request_switch_card(player_idx)
                if self.config.history_level > 0:
                    self._save_history()
            elif self.state == MatchState.STARTING_CARD_SWITCH:
                self._set_match_state(MatchState.STARTING_CHOOSE_CHARACTOR)
                for player_idx in range(len(self.player_tables)):
                    self._request_choose_charactor(player_idx)
                if self.config.history_level > 0:
                    self._save_history()
            elif self.state == MatchState.STARTING_CHOOSE_CHARACTOR:
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
                raise NotImplementedError(
                    f'Match state {self.state} not implemented.')
            """
            Record history.
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
        logging.info(f'Response received: {response}')
        if len(self.requests) == 0:
            raise ValueError('Match is not waiting for response.')
        # check if the response is valid
        if not response.is_valid(self):
            raise ValueError('Response is not valid.')
        # check if the request exist
        if not self.check_request_exist(response.request):
            raise ValueError('Request does not exist.')
        # clear prediction after receiving response
        self.skill_predictions.clear()
        # call different respond functions based on the type of response
        if isinstance(response, SwitchCharactorResponse):
            self._respond_switch_charactor(response)
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
        elif isinstance(response, ChooseCharactorResponse):
            self._respond_choose_charactor(response)
        elif isinstance(response, RerollDiceResponse):
            self._respond_reroll_dice(response)
        else:
            raise AssertionError(
                f'Response type {type(response)} not recognized.')

    def is_game_end(self) -> bool:
        """
        Check if the game reaches end condition. If game is ended, it will
        set `self.winner` to the winner of the game.
        PVE may have different end condition with PVP, and currently not
        supported.

        Returns:
            bool: True if game reaches end condition, False otherwise.
        """
        # all charactors are defeated
        for pnum, table in enumerate(self.player_tables):
            for charactor in table.charactors:
                if charactor.is_alive:
                    break
            else:
                assert len(self.player_tables) == 2
                self.winner = 1 - pnum
                return True
        return False

    def _next_action(self):
        """
        Do one action in `self.event_frames`. If the last event frame has
        triggered actions, it will do one action and stack new event frame.
        If triggered actions is empty and has triggerred objects, get 
        actions and do the first. If have unprocessed event arguments,
        trigger objects. If none of all, pop last event frame.
        Unless there are no actions, this function will exactly do one action.
        """
        assert len(self.event_frames) > 0, 'No event frame to process.'
        while len(self.event_frames):
            event_frame = self.event_frames[-1]
            if len(event_frame.triggered_actions):
                # do one action
                activated_action = event_frame.triggered_actions.pop(0)
                logging.info(f'Action activated: {activated_action}')
                event_args = self._act(activated_action)
                self._stack_events(event_args)
                return
            elif len(event_frame.triggered_objects):
                # get actions
                event_arg = event_frame.processing_event
                assert event_arg is not None
                object_position = event_frame.triggered_objects.pop(0)
                object = self.get_object(object_position, event_arg.type)
                object_name = object.__class__.__name__
                if hasattr(object, 'name'):
                    object_name = object.name  # type: ignore
                if object is None:
                    logging.warning(
                        f'Object {object_position} does not exist. '
                        'Is it be removed before triggering or a bug?'
                    )
                else:
                    handler_name = f'event_handler_{event_arg.type.name}'
                    func = getattr(object, handler_name, None)
                    assert func is not None, (
                        f'Object {object_name} does not have handler for '
                        f'{event_arg.type.name}.'
                    )
                    event_frame.triggered_actions = func(event_arg, self)
                    if event_frame.triggered_actions is None:
                        raise AssertionError(
                            f'Object {object_name} with event '
                            f'{event_arg.type} returns None.'
                        )
                    if len(event_frame.triggered_actions) > 0:
                        logging.info(
                            f'Object {object_name} with event {event_arg.type}'
                            f', triggered '
                            f'{len(event_frame.triggered_actions)} actions '
                        )
            elif len(event_frame.events):
                # trigger objects
                self._trigger_event(event_frame)
            else:
                # pop event frame
                self.event_frames.pop()
        # event frame cleared, clear trashbin
        self.trashbin.clear()

    def _game_start(self):
        """
        Game started. Will send game start event.
        """
        event = GameStartEventArguments(
            player_go_first = self.current_player,
        )
        self._stack_event(event)

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
                player_idx = pnum,
                position = ObjectPosition(
                    player_idx = pnum,
                    area = ObjectPositionType.SYSTEM,
                    id = 0,
                ),
            )
            self._modify_value(initial_color_value, 'REAL')
            initial_color_value.dice_colors = initial_color_value.dice_colors[
                :self.config.initial_dice_number
            ]
            random_number = (
                self.config.initial_dice_number 
                - len(initial_color_value.dice_colors)
            )
            color_dict: Dict[DieColor, int] = {}
            for color in initial_color_value.dice_colors:
                color_dict[color] = color_dict.get(color, 0) + 1
            for color, num in color_dict.items():
                event_args += self._act(CreateDiceAction(
                    player_idx = pnum,
                    number = num,
                    color = color
                ))
            event_args += self._act(CreateDiceAction(
                player_idx = pnum,
                number = random_number,
                random = True
            ))
        event_frame = EventFrame(
            events = event_args,
        )
        self.empty_frame_assertion(
            event_frame, 
            'Create dice in round start should not trigger actions.'
        )
        # collect actions triggered by round start
        # reroll dice chance. reroll times can be modified by objects.
        for pnum, player_table in enumerate(self.player_tables):
            reroll_times = self.config.initial_dice_reroll_times
            reroll_value = RerollValue(
                position = ObjectPosition(
                    player_idx = pnum,
                    area = ObjectPositionType.SYSTEM,
                    id = 0,
                ),
                value = reroll_times,
                player_idx = pnum,
            )
            self._modify_value(reroll_value, mode = 'REAL')
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
            player_go_first = self.current_player,
            round = self.round_number,
            dice_colors = [table.dice.colors.copy()
                           for table in self.player_tables],
        )
        event_frame = self._stack_event(event_arg)
        logging.info(
            f'In round prepare, {len(event_frame.triggered_objects)} '
            f'handlers triggered.'
        )

    def _player_action_start(self):
        """
        Start a player's action phase. Will generate action phase start event.  
        """
        not_all_declare_end = False
        for table in self.player_tables:
            if not table.has_round_ended:
                not_all_declare_end = True
        assert not_all_declare_end, 'All players have declared round end.'
        event = PlayerActionStartEventArguments(
            player_idx = self.current_player)
        self._stack_event(event)

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
        self._request_switch_charactor(self.current_player)
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
            # PLAYER_ACTION_START in next step, and trigger correcponding event
            self._set_match_state(MatchState.ROUND_PREPARING)

    def _round_ending(self):
        """
        End a round. Will stack round end event.
        """
        event = RoundEndEventArguments(
            player_go_first = self.current_player,
            round = self.round_number,
            initial_card_draw = self.config.initial_card_draw
        )
        self._stack_event(event)

    def get_object(
        self, position: ObjectPosition, action: ActionTypes | None = None
    ) -> ObjectBase | None:
        """
        Get object by its position. If obect not exist, return None.
        When action is specified, it will check trashbin and find objects that
        can handle the action.
        """
        assert position.area != ObjectPositionType.INVALID, 'Invalid area.'
        if position.area == ObjectPositionType.SYSTEM:
            for object in self.event_handlers:
                if object.id == position.id:
                    return object
            raise NotImplementedError('Currently should not be None')
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
        2. objects belongs to charactor goes first
            2.1. active charactor first, otherwise the default order.
            2.2. for one charactor, order is weapon, artifact, talent, status.
            2.3. for status, order is their index in status list, i.e. 
                generated time.
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

    def _stack_event(
        self, event_arg: EventArguments,
    ) -> EventFrame:
        """
        stack a new event. It will wrap it into a list and call 
        self._trigger_events.
        """
        return self._stack_events([event_arg])

    def _stack_events(
        self, event_args: List[EventArguments],
    ) -> EventFrame:
        """
        stack events. It will create a new EventFrame with events and
        append it into self.event_frames. Then it will return the event frame.
        """
        frame = EventFrame(
            events = event_args,
        )
        self.event_frames.append(frame)
        return frame

    def _trigger_event(
        self, event_frame: EventFrame,
    ) -> EventArguments:
        """
        trigger new event to update triggered object lists of a EventFrame.
        it will take first event from events, put it into processing_event,
        and update triggered object lists.
        """
        assert len(event_frame.triggered_objects) == 0
        assert len(event_frame.triggered_actions) == 0
        assert len(event_frame.events) != 0
        event_arg = event_frame.events.pop(0)
        event_frame.processing_event = event_arg
        object_list = self.get_object_list()
        # add object in trashbin to list
        for object in self.trashbin:
            if event_arg.type in object.available_handler_in_trashbin:
                object_list.append(object)
        handler_name = f'event_handler_{event_arg.type.name}'
        for obj in object_list:
            # for deck objects, check availability
            if obj.position.area == ObjectPositionType.DECK:
                if event_arg.type not in obj.available_handler_in_deck:
                    continue
            name = obj.__class__.__name__
            if hasattr(obj, 'name'):  # pragma: no cover
                name = obj.name  # type: ignore
            func = getattr(obj, handler_name, None)
            if func is not None:
                logging.debug(f'Trigger event {event_arg.type.name} '
                              f'for {name}.')
                event_frame.triggered_objects.append(obj.position)
        return event_arg

    def _modify_value(self, value: ModifiableValueBase, 
                      mode: Literal['TEST', 'REAL'],
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
        if mode == 'TEST':
            assert value.type == ModifiableValueTypes.COST, (
                'Only cost can be modified in test mode.'
            )
        object_list = self.get_object_list()
        modifier_name = f'value_modifier_{value.type.name}'
        for obj in object_list:
            name = obj.__class__.__name__
            if hasattr(obj, 'name'):  # pragma: no cover
                name = obj.name  # type: ignore
            func = getattr(obj, modifier_name, None)
            if func is not None:
                logging.debug(f'Modify value {value.type.name} for {name}.')
                value = func(value, self, mode)

    def _predict_skill(self, player_idx: int) -> None:
        """
        Predict skill results of a player. If config.make_skill_prediction,
        it will predict the results when a skill is used, regardless of the
        skill availability, except for skills that can never be used by player.
        The predict results are saved in self.skill_predictions, with the 
        player idx, charactor idx, skill idx, and diff of the match after
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
        copy = self.copy(deep = True, exclude = {'_history', '_history_diff'})
        self._history += history
        self._history_diff += history_diff
        # disable history logging and skill prediction for copy
        copy._prediction_mode = True
        table = copy.player_tables[player_idx]
        charactor = table.charactors[table.active_charactor_idx]
        skills = charactor.skills
        for sidx, skill in enumerate(skills):
            if not skill.is_valid(self):
                continue
            # a valid skill, try to use it
            one_copy = copy.copy(deep = True)
            one_copy._respond_use_skill(UseSkillResponse(
                request = UseSkillRequest(
                    player_idx = player_idx,
                    charactor_idx = table.active_charactor_idx,
                    skill_idx = sidx,
                    dice_colors = [],
                    cost = Cost(original_value = Cost()),
                ),
                dice_idxs = []
            ))
            one_copy.step()
            # get diff after prediction
            diff = list(dictdiffer.diff(copy.dict(), one_copy.dict()))
            # remove prev values of 'remove' in diff
            for d in diff:
                if d[0] == 'remove':
                    for i in range(len(d[2])):
                        d[2][i] = (d[2][i][0], None)
            self.skill_predictions.append({
                'player_idx': player_idx,
                'charactor_idx': table.active_charactor_idx,
                'skill_idx': sidx,
                'diff': diff
            })

    """
    Request functions. To generate specific requests.
    """

    def _request_switch_card(self, player_idx: int):
        """
        Generate switch card requests.
        """
        table = self.player_tables[player_idx]
        self.requests.append(SwitchCardRequest(
            player_idx = player_idx,
            card_names = [card.name for card in table.hands]
        ))

    def _request_choose_charactor(self, player_idx: int):
        """
        Generate switch card requests.
        """
        table = self.player_tables[player_idx]
        available: List[int] = []
        for cnum, charactor in enumerate(table.charactors):
            if charactor.is_alive:
                available.append(cnum)
        self.requests.append(ChooseCharactorRequest(
            player_idx = player_idx,
            available_charactor_idxs = available
        ))

    def _request_reroll_dice(self, player_idx: int, reroll_number: int):
        """
        reroll by game actions cannot be modified
        """
        if reroll_number <= 0:
            return
        player_table = self.player_tables[player_idx]
        self.requests.append(RerollDiceRequest(
            player_idx = player_idx,
            colors = player_table.dice.colors.copy(),
            reroll_times = reroll_number
        ))

    def _request_switch_charactor(self, player_idx: int):
        """
        Generate switch charactor requests.
        """
        table = self.player_tables[player_idx]
        active_charactor = table.charactors[table.active_charactor_idx]
        for cidx, charactor in enumerate(table.charactors):
            if cidx == table.active_charactor_idx or charactor.is_defeated:
                continue
            dice_cost = Cost(any_dice_number = 1)
            dice_cost.label = CostLabels.SWITCH_CHARACTOR.value
            dice_cost_value = CostValue(
                cost = dice_cost,
                position = active_charactor.position,
                target_position = charactor.position
            )
            self._modify_value(dice_cost_value, mode = 'TEST')
            charge, arcane_legend = table.get_charge_and_arcane_legend()
            if not dice_cost_value.cost.is_valid(
                dice_colors = table.dice.colors,
                charge = charge,
                arcane_legend = arcane_legend,
                strict = False,
            ):
                continue
            self.requests.append(SwitchCharactorRequest(
                player_idx = player_idx,
                active_charactor_idx = table.active_charactor_idx,
                target_charactor_idx = cidx,
                dice_colors = table.dice.colors.copy(),
                cost = dice_cost_value.cost,
            ))

    def _request_elemental_tuning(self, player_idx: int):
        table = self.player_tables[player_idx]
        target_color = ELEMENT_TO_DIE_COLOR[
            table.charactors[table.active_charactor_idx].element
        ]
        available_dice_idx = [
            didx for didx, color in enumerate(table.dice.colors)
            if color != target_color and color != DieColor.OMNI
        ]
        if self.config.recreate_mode:
            # in recreate mode, all dice can be tuned
            available_dice_idx = list(range(len(table.dice.colors)))
        available_card_idxs = list(range(len(table.hands)))
        if len(available_dice_idx) and len(available_card_idxs):
            self.requests.append(ElementalTuningRequest(
                player_idx = player_idx,
                dice_colors = table.dice.colors.copy(),
                dice_idxs = available_dice_idx,
                card_idxs = available_card_idxs
            ))

    def _request_declare_round_end(self, player_idx: int):
        self.requests.append(DeclareRoundEndRequest(
            player_idx = player_idx
        ))

    def _request_use_skill(self, player_idx: int):
        """
        Generate use skill requests. If active charactor is stunned, or
        not satisfy the condition to use skill, it will skip generating
        request.
        """
        table = self.player_tables[player_idx]
        front_charactor = table.charactors[table.active_charactor_idx]
        if front_charactor.is_stunned:
            # stunned, cannot use skill.
            return
        for sid, skill in enumerate(front_charactor.skills):
            if skill.is_valid(self):
                cost = skill.cost.copy(deep = True)
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
                    cost = cost,
                    position = skill.position,
                    target_position = None
                )
                self._modify_value(cost_value, mode = 'TEST')
                dice_colors = table.dice.colors
                if cost_value.cost.is_valid(
                    dice_colors = dice_colors, 
                    charge = front_charactor.charge,
                    arcane_legend = table.arcane_legend,
                    strict = False
                ):
                    self.requests.append(UseSkillRequest(
                        player_idx = player_idx,
                        charactor_idx = table.active_charactor_idx,
                        skill_idx = sid,
                        dice_colors = dice_colors.copy(),
                        cost = cost_value.cost
                    ))

    def _request_use_card(self, player_idx: int):
        table = self.player_tables[player_idx]
        cards = table.hands
        for cid, card in enumerate(cards):
            if card.is_valid(self):
                cost = card.cost.copy(deep = True)
                cost_value = CostValue(
                    cost = cost,
                    position = card.position,
                    target_position = None
                )
                self._modify_value(cost_value, mode = 'TEST')
                dice_colors = table.dice.colors
                charge, arcane_legend = table.get_charge_and_arcane_legend()
                if cost_value.cost.is_valid(
                    dice_colors = dice_colors, 
                    charge = charge,
                    arcane_legend = arcane_legend,
                    strict = False
                ):
                    self.requests.append(UseCardRequest(
                        player_idx = player_idx,
                        card_idx = cid,
                        dice_colors = dice_colors.copy(),
                        cost = cost_value.cost,
                        targets = list(card.get_targets(self))
                    ))

    """
    Response functions. To deal with specific responses.
    """

    def _respond_switch_card(self, response: SwitchCardResponse):
        """
        TODO: generate a event frame with action queues.
        """
        # restore cards
        event_args: List[EventArguments] = []
        event_args += self._act(RestoreCardAction(
            player_idx = response.player_idx,
            card_idxs = response.card_idxs
        ))
        event_args += self._act(
            DrawCardAction(
                player_idx = response.player_idx,
                number = len(response.card_idxs),
                blacklist_names = response.card_names,
                draw_if_filtered_not_enough = True
            )
        )
        event_frame = self._stack_events(event_args)
        self.empty_frame_assertion(
            event_frame,
            'Switch card should not trigger actions now.'
        )
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_idx != response.player_idx
        ]

    def _respond_choose_charactor(self, response: ChooseCharactorResponse):
        event_args = self._act(
            ChooseCharactorAction.from_response(response)
        )
        self._stack_events(event_args)
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_idx != response.player_idx
        ]

    def _respond_reroll_dice(self, response: RerollDiceResponse):
        """
        Deal with reroll dice response. If there are still reroll times left,
        keep request and only substrat reroll times. If there are no reroll
        times left, remove request.
        TODO: generate a event frame with action queues.
        """
        event_args = self._action_remove_dice(RemoveDiceAction.from_response(
            response
        ))
        event_frame = self._stack_events(list(event_args))
        self.empty_frame_assertion(
            event_frame, 
            'Removing dice in Reroll Dice should not trigger actions.'
        )
        event_args = self._action_create_dice(CreateDiceAction(
            player_idx = response.player_idx,
            number = len(response.reroll_dice_idxs),
            random = True,
        ))
        event_frame = self._stack_events(list(event_args))
        self.empty_frame_assertion(
            event_frame, 
            'Creating dice in Reroll Dice should not trigger actions.'
        )
        # modify request
        for num, req in enumerate(self.requests):  # pragma: no branch
            if isinstance(req, RerollDiceRequest):  # pragma: no branch
                if req.player_idx == response.player_idx:  # pragma: no branch
                    if req.reroll_times > 1:
                        req.reroll_times -= 1
                        req.colors = self.player_tables[
                            response.player_idx].dice.colors.copy()
                    else:
                        self.requests.pop(num)
                    break

    def _respond_switch_charactor(self, response: SwitchCharactorResponse):
        """
        Deal with switch charactor response. If it is combat action, add
        combat action to action queue. Remove related requests.
        """
        actions: List[ActionBase] = []
        dice_idxs = response.dice_idxs
        if len(dice_idxs):
            actions.append(RemoveDiceAction(
                player_idx = response.player_idx,
                dice_idxs = dice_idxs,
            ))
        table = self.player_tables[response.player_idx]
        active_charactor = table.charactors[table.active_charactor_idx]
        target_charactors = table.charactors[
            response.request.target_charactor_idx]
        cost = response.request.cost.original_value
        cost_value = CostValue(
            position = active_charactor.position,
            cost = cost,
            target_position = target_charactors.position
        )
        self._modify_value(
            value = cost_value,
            mode = 'REAL'
        )
        actions.append(SwitchCharactorAction.from_response(response))
        actions.append(ActionEndAction(
            action_label = PlayerActionLabels.SWITCH.value,
            position = ObjectPosition(
                player_idx = response.player_idx,
                charactor_idx = response.request.active_charactor_idx,
                area = ObjectPositionType.CHARACTOR,
                id = self.player_tables[response.player_idx].charactors[
                    response.request.active_charactor_idx].id,
            ),
            do_combat_action = True
        ))
        event_frame = EventFrame(
            events = [],
            triggered_actions = actions
        )
        self.event_frames.append(event_frame)
        self.requests = [x for x in self.requests
                         if x.player_idx != response.player_idx]

    def _respond_elemental_tuning(self, response: ElementalTuningResponse):
        """
        Deal with elemental tuning response. It is splitted into 3 actions,
        remove one hand card, remove one die, and add one die.
        """
        die_idx = response.dice_idx
        table = self.player_tables[response.player_idx]
        actions: List[ActionBase] = []
        actions.append(RemoveCardAction(
            position = table.hands[response.card_idx].position,
            remove_type = 'BURNED'
        ))
        actions.append(RemoveDiceAction(
            player_idx = response.player_idx,
            dice_idxs = [die_idx]
        ))
        active_charactor = table.get_active_charactor()
        assert active_charactor is not None
        actions.append(CreateDiceAction(
            player_idx = response.player_idx,
            number = 1,
            color = ELEMENT_TO_DIE_COLOR[active_charactor.element]
        ))
        actions.append(ActionEndAction(
            action_label = PlayerActionLabels.TUNE.value,
            position = ObjectPosition(
                player_idx = response.player_idx,
                area = ObjectPositionType.SYSTEM,
                id = 0
            ),
            do_combat_action = False
        ))
        event_frame = EventFrame(
            events = [],
            triggered_actions = actions
        )
        self.event_frames.append(event_frame)
        self.requests = [x for x in self.requests
                         if x.player_idx != response.player_idx]

    def _respond_declare_round_end(self, response: DeclareRoundEndResponse):
        """
        Deal with declare round end response. It is splitted into 2 actions,
        declare round end and combat action.
        """
        actions: List[ActionBase] = []
        actions.append(DeclareRoundEndAction.from_response(response))
        actions.append(ActionEndAction(
            action_label = PlayerActionLabels.END.value,
            position = ObjectPosition(
                player_idx = response.player_idx,
                area = ObjectPositionType.SYSTEM,
                id = 0
            ),
            do_combat_action = True
        ))
        event_frame = EventFrame(
            events = [],
            triggered_actions = actions
        )
        self.event_frames.append(event_frame)
        self.requests = [x for x in self.requests
                         if x.player_idx != response.player_idx]

    def _respond_use_skill(self, response: UseSkillResponse):
        request = response.request
        skill = self.player_tables[response.player_idx].charactors[
            request.charactor_idx].skills[request.skill_idx]
        cost = response.request.cost.original_value
        cost_value = CostValue(
            position = skill.position,
            cost = cost,
            target_position = None
        )
        self._modify_value(
            value = cost_value,
            mode = 'REAL'
        )
        action_label, combat_action = skill.get_action_type(self)
        actions: List[Actions] = [
            RemoveDiceAction(
                player_idx = response.player_idx,
                dice_idxs = response.dice_idxs,
            ),
            UseSkillAction(
                skill_position = skill.position,
            ),
            SkillEndAction(
                position = skill.position,
                target_position = self.player_tables[
                    1 - skill.position.player_idx
                ].get_active_charactor().position,
                skill_type = skill.skill_type
            ),
            ActionEndAction(
                action_label = action_label,
                position = skill.position,
                do_combat_action = combat_action
            )
        ]
        event_frame = EventFrame(
            events = [],
            triggered_actions = actions
        )
        self.event_frames.append(event_frame)
        self.requests = [x for x in self.requests
                         if x.player_idx != response.player_idx]

    def _respond_use_card(self, response: UseCardResponse):
        request = response.request
        table = self.player_tables[response.player_idx]
        card = table.hands[request.card_idx]
        cost = response.request.cost.original_value
        cost_value = CostValue(
            position = card.position,
            cost = cost,
            target_position = None
        )
        self._modify_value(
            value = cost_value,
            mode = 'REAL'
        )
        actions: List[Actions] = [
            RemoveDiceAction(
                player_idx = response.player_idx,
                dice_idxs = response.dice_idxs,
            ),
            UseCardAction(
                card_position = card.position,
                target = response.target,
            )
        ]
        action_label, combat_action = card.get_action_type(self)
        actions.append(ActionEndAction(
            action_label = action_label,
            position = card.position,
            do_combat_action = combat_action
        ))
        event_frame = EventFrame(
            events = [],
            triggered_actions = actions
        )
        self.event_frames.append(event_frame)
        self.requests = [x for x in self.requests
                         if x.player_idx != response.player_idx]

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
        if isinstance(action, ChooseCharactorAction):
            return list(self._action_choose_charactor(action))
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
        elif isinstance(action, SwitchCharactorAction):
            return list(self._action_switch_charactor(action))
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
        elif isinstance(action, CharactorDefeatedAction):
            return list(self._action_charactor_defeated(action))
        elif isinstance(action, CreateObjectAction):
            return list(self._action_create_object(action))
        elif isinstance(action, RemoveObjectAction):
            return list(self._action_remove_object(action))
        elif isinstance(action, ChangeObjectUsageAction):
            return list(self._action_change_object_usage(action))
        elif isinstance(action, MoveObjectAction):
            return list(self._action_move_object(action))
        elif isinstance(action, ConsumeArcaneLegendAction):
            return list(self._action_consume_arcane_legend(action))
        elif isinstance(action, GenerateChooseCharactorRequestAction):
            return list(self._action_generate_choose_charactor_request(action))
        elif isinstance(action, GenerateRerollDiceRequestAction):
            return list(self._action_generate_reroll_dice_request(action))
        elif isinstance(action, SkipPlayerActionAction):
            return list(self._action_skip_player_action(action))
        elif isinstance(action, CharactorReviveAction):
            return list(self._action_charactor_revive(action))
        elif isinstance(action, GenerateSwitchCardRequestAction):
            return list(self._action_generate_switch_card_request(action))
        else:
            self._set_match_state(MatchState.ERROR)  # pragma no cover
            raise AssertionError(f'Unknown action {action}.')

    def _action_draw_card(
            self, 
            action: DrawCardAction) -> List[DrawCardEventArguments]:
        """
        Draw cards from the deck, and return the argument of triggered events.
        Can set blacklist or whitelist to filter cards. Cannot set both.
        If writelist is set, card should satisfy all whitelists.
        If blacklist is set, card should satisfy no blacklist.
        If available cards are less than number, draw all available cards, 
        and if draw_if_not_enough is set True, randomly draw cards until
        number is reached or deck is empty.
        """
        player_idx = action.player_idx
        number = action.number
        table = self.player_tables[player_idx]
        if len(table.table_deck) < number:
            number = len(table.table_deck)
        draw_cards: List[CardBase] = []
        blacklist: List[CardBase] = []
        if self.version <= '0.0.1':
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
                raise AssertionError('Whitelist and blacklist cannot be both '
                                     'specified.')
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
                'Blacklist should be empty in recreate mode. Please check '
                'card order.'
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
                'Blacklist should be empty in recreate mode. Please check '
                'card order.'
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
        names = [x.name for x in table.table_deck[:number]]
        for card in draw_cards:
            card.position = card.position.set_area(ObjectPositionType.HAND)
        table.hands.extend(draw_cards)
        logging.info(
            f'Draw card action, player {player_idx}, number {number}, '
            f'cards {names}, '
            f'deck size {len(table.table_deck)}, hand size {len(table.hands)}'
        )
        event_arg = DrawCardEventArguments(
            action = action,
            hand_size = len(table.hands),
            max_hand_size = self.config.max_hand_size,
        )
        return [event_arg]

    def _action_restore_card(
            self, 
            action: RestoreCardAction) -> List[RestoreCardEventArguments]:
        """
        Restore cards to the deck.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        card_idxs = action.card_idxs[:]
        card_idxs.sort(reverse = True)  # reverse order to avoid index error
        card_names = [table.hands[cidx].name for cidx in card_idxs]
        restore_cards: List[CardBase] = []
        for cidx in card_idxs:
            restore_cards.append(table.hands[cidx])
            table.hands = table.hands[:cidx] + table.hands[cidx + 1:]
        for card in restore_cards:
            card.position = card.position.set_area(ObjectPositionType.DECK)
        table.table_deck.extend(restore_cards)
        if self.version >= '0.0.2' and not self.config.recreate_mode:
            # after 0.0.2, deck is shuffled after restore cards
            self._random_shuffle(table.table_deck)
        logging.info(
            f'Restore card action, player {player_idx}, '
            f'number {len(card_idxs)}, cards: {card_names}, '
            f'deck size {len(table.table_deck)}, hand size {len(table.hands)}'
        )
        event_arg = RestoreCardEventArguments(
            action = action,
            card_names = card_names
        )
        return [event_arg]

    def _action_remove_card(self, action: RemoveCardAction) \
            -> List[RemoveCardEventArguments]:
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
                raise AssertionError(f'Cannot find card {card_id} in hand.')
            card = table.hands.pop(match_idx)
        # elif card_position == ObjectPositionType.DECK:
        #     card = table.table_deck.pop(action.card_idx)
        else:
            self._set_match_state(MatchState.ERROR)  # pragma no cover
            raise AssertionError(f'Unknown card position {card_position}.')
        logging.info(
            f'Remove hand card action, player {player_idx}, '
            f'card position {card_position}, '
            f'card name {card.name}, '
            f'remove type {remove_type}.'
        )
        event_arg = RemoveCardEventArguments(
            action = action,
            card_name = card.name
        )
        return [event_arg]

    def _action_choose_charactor(self, action: ChooseCharactorAction) \
            -> List[ChooseCharactorEventArguments]:
        """
        This action triggers by game start and by active charactor is defeated.
        Be care of differences between choose_charactor when implementing 
        event triggers.
        """
        player_idx = action.player_idx
        charactor_idx = action.charactor_idx
        table = self.player_tables[player_idx]
        logging.info(
            f'Choose charactor action, player {player_idx}, '
            f'charactor {charactor_idx}, '
            f'name {table.charactors[charactor_idx].name}'
        )
        original_charactor_idx = table.active_charactor_idx
        table.active_charactor_idx = charactor_idx
        # after choose charactor, add plunging mark
        table.plunge_satisfied = True
        event_arg = ChooseCharactorEventArguments(
            action = action,
            original_charactor_idx = original_charactor_idx
        )
        return [event_arg]

    def _action_create_dice(self, action: CreateDiceAction) \
            -> List[CreateDiceEventArguments]:
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
            raise ValueError('Dice cannot be both random and different.')
        candidates: List[DieColor] = [
            DieColor.CRYO, DieColor.PYRO, DieColor.HYDRO, DieColor.ELECTRO,
            DieColor.GEO, DieColor.DENDRO, DieColor.ANEMO
        ]
        # generate dice based on color
        if is_random:
            candidates.append(DieColor.OMNI)  # random, can be omni
            for _ in range(number):
                selected_color = candidates[int(self._random() 
                                                * len(candidates))]
                dice.append(selected_color)
        elif is_different:
            if number > len(candidates):
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise ValueError('Not enough dice colors.')
            self._random_shuffle(candidates)
            candidates = candidates[:number]
            for selected_color in candidates:
                dice.append(selected_color)
        else:
            if color is None:
                self._set_match_state(MatchState.ERROR)  # pragma no cover
                raise ValueError('Dice color should be specified.')
            for _ in range(number):
                dice.append(color)
        # if there are more dice than the maximum, discard the rest
        max_obtainable_dice = (self.config.max_dice_number 
                               - len(table.dice.colors))
        table.dice.colors += dice[:max_obtainable_dice]
        # sort dice by color
        table.sort_dice()
        logging.info(
            f'Create dice action, player {player_idx}, '
            f'number {len(dice)}, '
            f'dice colors {dice}, '
            f'obtain {len(dice[:max_obtainable_dice])}, '
            f'over maximum {len(dice[max_obtainable_dice:])}, '
            f'current dice on table {table.dice}'
        )
        return [CreateDiceEventArguments(
            action = action,
            colors_generated = dice[:max_obtainable_dice],
            colors_over_maximum = dice[max_obtainable_dice:]
        )]

    def _action_remove_dice(self, action: RemoveDiceAction) \
            -> List[RemoveDiceEventArguments]:
        player_idx = action.player_idx
        dice_idxs = action.dice_idxs
        table = self.player_tables[player_idx]
        removed_dice: List[DieColor] = []
        dice_idxs.sort(reverse = True)  # reverse order to avoid index error
        for idx in dice_idxs:
            removed_dice.append(table.dice.colors.pop(idx))
        # sort dice by color
        table.sort_dice()
        logging.info(
            f'Remove dice action, player {player_idx}, '
            f'number {len(dice_idxs)}, '
            f'dice colors {removed_dice.reverse()}, '
            f'current dice on table {table.dice}'
        )
        return [RemoveDiceEventArguments(
            action = action,
            colors_removed = removed_dice
        )]

    def _action_declare_round_end(self, action: DeclareRoundEndAction) \
            -> List[DeclareRoundEndEventArguments]:
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        logging.info(
            f'Declare round end action, player {player_idx}.'
        )
        table.has_round_ended = True
        return [DeclareRoundEndEventArguments(
            action = action
        )]

    def _action_action_end(self, action: ActionEndAction) \
            -> List[ActionEndEventArguments]:
        player_idx = self.current_player   
        combat_action_value = CombatActionValue(
            position = action.position,
            action_label = action.action_label,
            do_combat_action = action.do_combat_action
        )
        self._modify_value(
            value = combat_action_value,
            mode = 'REAL'
        )
        if (
            combat_action_value.original_value.do_combat_action
            and combat_action_value.action_label 
            & (PlayerActionLabels.END.value | PlayerActionLabels.SKILL.value)
            != 0
        ):
            # did any combat action that is not switch, remove plunging mark
            self.player_tables[player_idx].plunge_satisfied = False
        if not combat_action_value.do_combat_action:
            if action.do_combat_action:
                logging.info(
                    f'player {player_idx} did a combat action, but is '
                    f'modified as a quick action. current player '
                    f'is {self.current_player}.'
                )
            else:
                logging.info(
                    f'player {player_idx} did a quick action, current player '
                    f'is {self.current_player}.'
                )
            return [ActionEndEventArguments(
                action = action,
                do_combat_action = False
            )]
        if self.player_tables[1 - player_idx].has_round_ended and \
                not self.player_tables[player_idx].has_round_ended:
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
            f'player {player_idx} did a combat action, current player '
            f'is {self.current_player}.'
        )
        return [ActionEndEventArguments(
            action = action,
            do_combat_action = True
        )]

    def _action_switch_charactor(self, action: SwitchCharactorAction) \
            -> List[SwitchCharactorEventArguments]:
        """
        This action triggers by player manually declare charactor switch
        or by using skills or by overloaded. Be care of differences between
        choose_charactor when implementing event triggers.
        """
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        current_active_idx = table.active_charactor_idx
        current_active_name = table.charactors[current_active_idx].name
        charactor_idx = action.charactor_idx
        charactor_name = table.charactors[charactor_idx].name
        if table.charactors[charactor_idx].is_defeated:
            self._set_match_state(MatchState.ERROR)  # pragma: no cover
            raise AssertionError(
                f'Cannot switch to defeated charactor {charactor_name}.'
            )
        if table.active_charactor_idx == charactor_idx:
            self._set_match_state(MatchState.ERROR)  # pragma: no cover
            raise AssertionError(
                f'Cannot switch to the active charactor {charactor_name}.'
            )
        logging.info(
            f'player {player_idx} '
            f'from charactor {current_active_name}:{current_active_idx} '
            f'switched to charactor {charactor_name}:{charactor_idx}.'
        )
        table.active_charactor_idx = charactor_idx
        # after charactor switch, add plunging mark
        table.plunge_satisfied = True
        return [SwitchCharactorEventArguments(
            action = action,
            last_active_charactor_idx = current_active_idx,
        )]

    def _action_make_damage(self, action: MakeDamageAction) \
            -> List[ReceiveDamageEventArguments | MakeDamageEventArguments 
                    | AfterMakeDamageEventArguments 
                    | SwitchCharactorEventArguments]:
        """
        Make damage action. It contains make damage, heal and element 
        application. It will return two types of events:
        1. MakeDamageEventArguments: All damage information dealt by this 
            action.
        2. SwitchCharactorEventArguments: If this damage action contains
            charactor change, i.e. overloaded, Skills of Anemo charactors, etc.
            A SwitchCharactorEventArguments will be generated.
            NOTE: only charactor switch of charactor received this damage will
            trigger this event, charactor switch of attacker (Kazuha, Kenki, 
            When the Crane Returned) should be another SwtichCharactorAction.
        NOTE: side effects by elemental reaction is handled by system event
        handler, which is listening ReceiveDamageEventArguments.
        """
        damage_lists = action.damage_value_list[:]
        switch_charactor: List[int] = action.charactor_change_idx
        events: List[ReceiveDamageEventArguments | MakeDamageEventArguments 
                     | AfterMakeDamageEventArguments
                     | SwitchCharactorEventArguments] = []
        infos: List[ReceiveDamageEventArguments] = []
        while len(damage_lists) > 0:
            damage = damage_lists.pop(0)
            damage_original = damage.copy(deep = True)
            assert (
                damage.target_position.area == ObjectPositionType.CHARACTOR
            ), (
                'Damage target position should be charactor.'
            )
            table = self.player_tables[damage.target_position.player_idx]
            charactor = table.charactors[damage.target_position.charactor_idx]
            assert charactor.is_alive, (
                'Damage target charactor should be alive.'
            )
            self._modify_value(damage, 'REAL')
            damage_element_type = DAMAGE_TYPE_TO_ELEMENT[
                damage.damage_elemental_type]
            target_element_application = charactor.element_application
            [elemental_reaction, reacted_elements, applied_elements] = \
                check_elemental_reaction(
                    damage_element_type, 
                    target_element_application
            )
            if (elemental_reaction is ElementalReactionType.OVERLOADED
                    and damage.target_position.charactor_idx 
                    == table.active_charactor_idx):
                # overloaded to next charactor
                player_idx = damage.target_position.player_idx
                assert switch_charactor[player_idx] == -1, (
                    'When overloaded to switch charactor, which already '
                    'contain charactor switch rule.'
                )
                nci = table.next_charactor_idx()
                if nci is not None:
                    switch_charactor[player_idx] = nci
            # apply elemental reaction, update damage and append new damages
            damage, new_damages = apply_elemental_reaction(
                table.charactors,
                table.active_charactor_idx,
                damage, 
                elemental_reaction, 
                reacted_elements,
            )
            damage_lists += new_damages
            # apply 3-step damage modification
            self._modify_value(damage, 'REAL')
            damage = DamageMultiplyValue.from_increase_value(damage)
            self._modify_value(damage, 'REAL')
            damage = DamageDecreaseValue.from_multiply_value(damage)
            self._modify_value(damage, 'REAL')
            # apply final damage and applied elements
            hp_before = charactor.hp
            charactor.hp -= damage.damage
            if charactor.hp < 0:
                charactor.hp = 0
            if charactor.hp > charactor.max_hp:
                charactor.hp = charactor.max_hp
            charactor.element_application = applied_elements
            infos.append(ReceiveDamageEventArguments(
                action = action,
                original_damage = damage_original,
                final_damage = damage,
                hp_before = hp_before,
                hp_after = charactor.hp,
                elemental_reaction = elemental_reaction,
                reacted_elements = reacted_elements,
            ))
        for info in infos:
            if info.final_damage.damage_type == DamageType.ELEMENT_APPLICATION:
                # ignore element application
                continue
            target = info.final_damage.target_position
            pidx = target.player_idx
            cidx = target.charactor_idx
            if pidx not in self.action_info:
                self.action_info[pidx] = {}
            if cidx not in self.action_info[pidx]:
                self.action_info[pidx][cidx] = []
            damage_type = info.final_damage.damage_elemental_type
            damage = info.final_damage.damage
            if damage_type == DamageElementalType.HEAL:
                damage = - damage
            self.action_info[pidx][cidx].append({
                'type': damage_type,
                'damage': damage,
            })
        make_damage_event = MakeDamageEventArguments(
            action = action,
            damages = infos,
        )
        events.append(make_damage_event)
        events += infos
        events.append(AfterMakeDamageEventArguments.
                      from_make_damage_event_arguments(make_damage_event))
        for table, sc in zip(self.player_tables, switch_charactor):
            if sc != -1 and sc != table.active_charactor_idx:
                # charactor switch
                sw_action = SwitchCharactorAction(
                    player_idx = table.player_idx,
                    charactor_idx = sc,
                )
                sw_events = self._action_switch_charactor(sw_action)
                events += sw_events
        return events

    def _action_charge(self, action: ChargeAction) \
            -> List[ChargeEventArguments]:
        player_idx = action.player_idx
        table = self.player_tables[player_idx]
        charactor = table.charactors[action.charactor_idx]
        if charactor.is_defeated:
            # charge defeated charactor
            logging.warning(
                f'tried to charge a defeated charactor! '
                f'player {player_idx} '
                f'charactor {charactor.name}:{action.charactor_idx}. '
                f'bug or defeated before charging?'
            )
            # ignore this action and return empty event arguments
            return []
        logging.info(
            f'player {player_idx} '
            f'charactor {charactor.name}:{table.active_charactor_idx} '
            f'charged {action.charge}.'
        )
        old_charge = charactor.charge
        charactor.charge += action.charge
        if charactor.charge > charactor.max_charge:
            charactor.charge = charactor.max_charge
        # charge should not be negative, unless in prediction mode
        if self._prediction_mode:
            if charactor.charge < 0:
                charactor.charge = 0
        else:
            assert charactor.charge >= 0
        return [ChargeEventArguments(
            action = action,
            charge_before = old_charge,
            charge_after = charactor.charge,
        )]

    def _action_charactor_defeated(
        self, action: CharactorDefeatedAction
    ) -> List[CharactorDefeatedEventArguments | RemoveObjectEventArguments]:
        """
        Charactor defeated action, all equipments and status are removed, 
        and is marked as defeated. Currently not support PVE character
        disappear features. Event arguments returned contains
        CharactorDefeatedEventArguments and RemoveObjectEventArguments.
        """
        ret: List[
            CharactorDefeatedEventArguments | RemoveObjectEventArguments
        ] = []
        player_idx = action.player_idx
        charactor_idx = action.charactor_idx
        table = self.player_tables[player_idx]
        charactor = table.charactors[charactor_idx]
        assert charactor.is_defeated, (
            'Should marked as defeated charactor.'
        )
        logging.info(
            f'player {player_idx} '
            f'charactor {charactor.name}:{charactor_idx} '
            f'defeated.'
        )
        removed_objects = [
            charactor.weapon,
            charactor.artifact,
            charactor.talent,
        ] + charactor.status
        for obj in removed_objects:
            if obj is not None:
                ret.append(RemoveObjectEventArguments(
                    action = RemoveObjectAction(
                        object_position = obj.position,
                    ),
                    object_name = obj.name
                ))
                self.trashbin.append(obj)
        charactor.weapon = None
        charactor.artifact = None
        charactor.talent = None
        charactor.status = []
        charactor.element_application = []
        charactor.is_alive = False
        charactor.charge = 0
        need_switch = False
        if table.active_charactor_idx == charactor_idx:
            table.active_charactor_idx = -1  # reset active charactor
            need_switch = True
        ret.append(CharactorDefeatedEventArguments(
            action = action,
            need_switch = need_switch,
        ))
        return ret

    def _action_charactor_revive(self, action: CharactorReviveAction) \
            -> List[CharactorReviveEventArguments]:
        """
        Charactor revive action. A defeated charactor is revived.
        """
        player_idx = action.player_idx
        charactor_idx = action.charactor_idx
        table = self.player_tables[player_idx]
        charactor = table.charactors[charactor_idx]
        assert charactor.is_defeated, (
            'Cannot revive a living charactor.'
        )
        logging.info(
            f'player {player_idx} '
            f'charactor {charactor.name}:{charactor_idx} '
            f'revived with {action.revive_hp} HP.'
        )
        charactor.is_alive = True
        charactor.hp = action.revive_hp
        return [CharactorReviveEventArguments(
            action = action,
        )]

    def _action_create_object(self, action: CreateObjectAction) \
            -> List[CreateObjectEventArguments]:
        """
        Action for creating objects, e.g. status, summons, supports.
        Note some objects are not created but moved, e.g. equipments and 
        supports, for these objects, do not use this action.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # charactor_idx = action.object_position.charactor_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_class = TeamStatusBase
            target_list = table.team_status
            target_name = 'team status'
        elif action.object_position.area \
                == ObjectPositionType.CHARACTOR_STATUS:
            target_class = CharactorStatusBase
            target_list = table.charactors[
                action.object_position.charactor_idx].status
            charactor = table.charactors[action.object_position.charactor_idx]
            if charactor.is_defeated:
                logging.warning(
                    'Trying to create status for defeated charactor '
                    f'{action.object_position.player_idx}:'
                    f'{action.object_position.charactor_idx}:'
                    f'{charactor.name}. Is it be defeated before creating '
                    'or a bug?'
                )
                return []
            target_name = 'charactor status'
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_class = SummonBase
            target_list = table.summons
            target_name = 'summon'
        elif action.object_position.area == ObjectPositionType.HAND:
            assert len(table.hands) < self.config.max_hand_size, (
                'Cannot create hand card when hand is full.'
            )
            target_class = CardBase
            target_list = table.hands
            target_name = 'hand'
        # elif action.object_position.area == ObjectPositionType.SYSTEM:
        #     target_classes = SystemEventHandlers
        #     target_list = self.event_handlers
        #     target_name = 'system event handler'
        else:
            raise NotImplementedError(
                f'Create object action for area {action.object_position.area} '
                'is not implemented.'
            )
        args = action.object_arguments.copy()
        args['name'] = action.object_name
        args['position'] = action.object_position
        target_object = get_instance(
            target_class, args
        )
        if target_name != 'hand':
            # if not create hand, not allow to create same name object
            for csnum, current_object in enumerate(target_list):
                if current_object.name == target_object.name:
                    # have same name object, only update status usage
                    current_object.renew(target_object)  # type: ignore
                    logging.info(
                        f'player {player_idx} '
                        f'renew {target_name} {action.object_name}.'
                    )
                    return [CreateObjectEventArguments(
                        action = action,
                        create_result = 'RENEW',
                        create_idx = csnum,
                    )]
        if (target_name == 'summon' 
                and len(target_list) >= self.config.max_summon_number):
            # summon number reaches maximum
            logging.warning(
                f'player {player_idx} '
                f'tried to create new {target_name} {action.object_name}, '
                f'but summon number reaches maximum '
                f'{self.config.max_summon_number}, and will not create '
                'the summon.'
            )
            return []
        logging.info(
            f'player {player_idx} '
            f'created new {target_name} {action.object_name}.'
        )
        target_list.append(target_object)  # type: ignore
        return [CreateObjectEventArguments(
            action = action,
            create_result = 'NEW',
            create_idx = len(target_list) - 1,
        )]

    def _action_remove_object(self, action: RemoveObjectAction) \
            -> List[RemoveObjectEventArguments]:
        """
        Action for removing objects, e.g. status, summons, supports.
        It supports removing equipments and supports.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # charactor_idx = action.object_position.charactor_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_list = table.team_status
            target_name = 'team status'
        elif action.object_position.area \
                == ObjectPositionType.CHARACTOR_STATUS:
            target_list = table.charactors[
                action.object_position.charactor_idx].status
            target_name = 'charactor status'
            assert table.charactors[
                action.object_position.charactor_idx].is_alive, (
                'Cannot remove status for defeated charactor now.'
            )
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_list = table.summons
            target_name = 'summon'
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            target_list = table.supports
            target_name = 'support'
        elif action.object_position.area == ObjectPositionType.CHARACTOR:
            # remove artifact, weapon or talent
            charactor = table.charactors[action.object_position.charactor_idx]
            assert charactor.is_alive, (
                'Cannot remove equips for defeated charactor now.'
            )
            removed_equip = None
            if charactor.weapon is not None and charactor.weapon.id == \
                    action.object_position.id:
                removed_equip = charactor.weapon
                charactor.weapon = None
                target_name = 'weapon'
            elif charactor.artifact is not None and charactor.artifact.id == \
                    action.object_position.id:
                removed_equip = charactor.artifact
                charactor.artifact = None
                target_name = 'artifact'
            elif charactor.talent is not None and charactor.talent.id == \
                    action.object_position.id:
                removed_equip = charactor.talent
                charactor.talent = None
                target_name = 'talent'
            else:
                raise AssertionError(
                    f'player {player_idx} tried to remove non-exist equipment '
                    f'from charactor {charactor.name} with id '
                    f'{action.object_position.id}.'
                )
            self.trashbin.append(removed_equip)  # type: ignore
            return [RemoveObjectEventArguments(
                action = action,
                object_name = removed_equip.name,
            )]
        else:
            raise NotImplementedError(
                f'Remove object action for area '
                f'{action.object_position.area} is not implemented.'
            )
        for csnum, current_object in enumerate(target_list):
            if current_object.id == action.object_position.id:
                # have same status, only update status usage
                removed_object = target_list.pop(csnum)
                logging.info(
                    f'player {player_idx} '
                    f'removed {target_name} {current_object.name}.'
                )
                self.trashbin.append(removed_object)  # type: ignore
                return [RemoveObjectEventArguments(
                    action = action,
                    object_name = current_object.name,
                )]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f'player {player_idx} '
            f'tried to remove non-exist {target_name} with id '
            f'{action.object_position.id}.'
        )

    def _action_change_object_usage(self, action: ChangeObjectUsageAction) \
            -> List[ChangeObjectUsageEventArguments]:
        """
        Action for changing object usage, e.g. status, summons, supports.
        """
        player_idx = action.object_position.player_idx
        table = self.player_tables[player_idx]
        # charactor_idx = action.object_position.charactor_id
        if action.object_position.area == ObjectPositionType.TEAM_STATUS:
            target_list = table.team_status
            target_name = 'team status'
        elif action.object_position.area == \
                ObjectPositionType.CHARACTOR_STATUS:
            target_list = table.charactors[
                action.object_position.charactor_idx].status
            target_name = 'charactor status'
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            target_list = table.supports
            target_name = 'support'
        elif action.object_position.area == ObjectPositionType.SUMMON:
            target_list = table.summons
            target_name = 'summon'
        else:
            raise NotImplementedError(
                f'Change object usage action for area '
                f'{action.object_position.area} is not implemented.'
            )
        for csnum, current_object in enumerate(target_list):
            if current_object.id == action.object_position.id:
                # have same status, only update status usage
                old_usage = current_object.usage
                new_usage = action.change_usage
                new_usage += old_usage
                new_usage = min(max(new_usage, action.min_usage),
                                action.max_usage)
                current_object.usage = new_usage
                logging.info(
                    f'player {player_idx} '
                    f'changed {target_name} {current_object.name} '
                    f'usage to {new_usage}.'
                )
                return [ChangeObjectUsageEventArguments(
                    action = action,
                    object_name = current_object.name,
                    usage_before = old_usage,
                    usage_after = new_usage,
                )]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f'player {player_idx} '
            f'tried to change non-exist {target_list} with id '
            f'{action.object_position.id}.'
        )
        return []

    def _action_move_object(self, action: MoveObjectAction) \
            -> List[MoveObjectEventArguments]:
        """
        Action for moving objects, e.g. equipments, supports.
        """
        player_idx = action.object_position.player_idx
        charactor_idx = action.object_position.charactor_idx
        table = self.player_tables[player_idx]
        assert (
            action.object_position.id == action.target_position.id
        ), (
            'Move object action should have same object id in both '
            'object position and target position.'
        )
        # charactor_idx = action.object_position.charactor_id
        if action.object_position.area == ObjectPositionType.HAND:
            assert table.using_hand is not None
            current_list = [table.using_hand]
            table.using_hand = None
            current_name = 'hand'
        elif action.object_position.area == ObjectPositionType.SUPPORT:
            current_list = table.supports
            current_name = 'support'
        elif action.object_position.area == ObjectPositionType.CHARACTOR:
            # move equipments
            charactor = table.charactors[charactor_idx]
            weapon = charactor.weapon
            artifact = charactor.artifact
            talent = charactor.talent
            if weapon is not None and weapon.id == action.object_position.id:
                charactor.weapon = None
                current_list = [weapon]
                current_name = 'weapon'
            elif artifact is not None and artifact.id == \
                    action.object_position.id:
                charactor.artifact = None
                current_list = [artifact]
                current_name = 'artifact'
            elif talent is not None and \
                    talent.id == action.object_position.id:
                raise NotImplementedError(
                    'Talent cannot be moved now.'
                )
                charactor.talent = None
                current_list = [talent]
                current_name = 'talent'
            else:
                raise AssertionError(
                    f'player {player_idx} tried to move non-exist equipment '
                    f'from charactor {charactor_idx} with id '
                    f'{action.object_position.id}.'
                )
        else:
            raise NotImplementedError(
                f'Move object action from area '
                f'{action.object_position.area} is not implemented.'
            )
        table = self.player_tables[action.target_position.player_idx]
        for csnum, current_object in enumerate(current_list):
            if current_object.id == action.object_position.id:
                if action.target_position.area == ObjectPositionType.HAND:
                    target_list = table.hands
                    target_name = 'hand'
                elif action.target_position.area == ObjectPositionType.SUPPORT:
                    target_list = table.supports
                    assert current_object.type == ObjectType.SUPPORT
                    assert (len(target_list) 
                            < self.config.max_support_number)
                    target_name = 'support'
                elif action.target_position.area \
                        == ObjectPositionType.CHARACTOR:
                    # quip equipments
                    assert (action.object_position.player_idx
                            == action.target_position.player_idx)
                    charactor = table.charactors[
                        action.target_position.charactor_idx
                    ]
                    assert charactor.is_alive, (
                        'Cannot equip to defeated charactor now.'
                    )
                    current_list.pop(csnum)
                    current_object.position = action.target_position
                    if current_object.type == ObjectType.ARTIFACT:
                        assert charactor.artifact is None
                        charactor.artifact = current_object  # type: ignore
                        target_name = 'artifact'
                    elif current_object.type == ObjectType.TALENT:
                        assert charactor.talent is None
                        charactor.talent = current_object  # type: ignore
                        target_name = 'talent'
                    elif current_object.type == ObjectType.WEAPON:
                        assert charactor.weapon is None
                        charactor.weapon = current_object  # type: ignore
                        target_name = 'weapon'
                    else:
                        raise NotImplementedError(
                            f'Move object action as eqipment with type '
                            f'{current_object.type} is not implemented.'
                        )
                    logging.info(
                        f'player {player_idx} '
                        f'moved {current_name} {current_object.name} '
                        f'to charactor {action.target_position.charactor_idx}'
                        f':{target_name}.'
                    )
                    return [MoveObjectEventArguments(
                        action = action,
                        object_name = current_object.name,
                    )]
                else:
                    raise NotImplementedError(
                        f'Move object action to area '
                        f'{action.target_position.area} is not implemented.'
                    )
                current_list.pop(csnum)
                current_object.position = action.target_position
                target_list.append(current_object)  # type: ignore
                logging.info(
                    f'player {player_idx} '
                    f'moved {current_name} {current_object.name} '
                    f'to {target_name}.'
                )
                return [MoveObjectEventArguments(
                    action = action,
                    object_name = current_object.name,
                )]
        self._set_match_state(MatchState.ERROR)  # pragma no cover
        raise AssertionError(
            f'player {player_idx} '
            f'tried to move non-exist {current_name} with id '
            f'{action.object_position.id}.'
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
        assert table.arcane_legend, (
            f'Arcane legend of player {player_idx} is consumed'
        )
        table.arcane_legend = False
        logging.info(
            f'player {player_idx} consumed arcane legend.'
        )
        return [ConsumeArcaneLegendEventArguments(
            action = action,
        )]

    """
    Action funtions that only used to trigger specific event
    """

    def _action_use_skill(self, action: UseSkillAction) \
            -> List[UseSkillEventArguments]:
        player_idx = action.skill_position.player_idx
        table = self.player_tables[player_idx]
        charactor = table.charactors[table.active_charactor_idx]
        skill = charactor.get_object(action.skill_position)
        assert skill is not None and skill.type == ObjectType.SKILL
        logging.info(
            f'player {player_idx} '
            f'charactor {charactor.name}:{table.active_charactor_idx} '
            f'use skill {skill.name}.'  # type: ignore
        )
        return [UseSkillEventArguments(
            action = action,
        )]

    def _action_use_card(self, action: UseCardAction) \
            -> List[UseCardEventArguments]:
        assert action.card_position.area == ObjectPositionType.HAND, (
            'Card should be used from hand.'
        )
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
                f'player {action.card_position.player_idx} '
                f'tried to use non-exist card with id '
                f'{action.card_position.id}.'
            )
        card = table.using_hand

        # check if use success
        use_card_value = UseCardValue(
            position = card.position,
            card = card
        )
        self._modify_value(use_card_value, 'REAL')

        info_str = (
            f'player {action.card_position.player_idx} '
            f'use card {card.name}.'  # type: ignore
        )
        if not use_card_value.use_card:
            info_str += ' But use card failed!'
        logging.info(info_str)

        return [UseCardEventArguments(
            action = action,
            card = card,
            use_card_success = use_card_value.use_card
        )]

    def _action_skill_end(self, action: SkillEndAction) \
            -> List[SkillEndEventArguments]:
        player_idx = action.position.player_idx
        charactor_idx = action.position.charactor_idx
        table = self.player_tables[player_idx]
        charactor = table.charactors[charactor_idx]
        logging.info(
            f'player {player_idx} '
            f'charactor {charactor.name}:{charactor_idx} '
            f'skill ended.'
        )
        return [SkillEndEventArguments(
            action = action,
        )]

    """
    Action functions that generate requests. Should not trigger event, i.e.
    return empty list.
    """

    def _action_generate_choose_charactor_request(
        self, action: GenerateChooseCharactorRequestAction
    ) -> List[EventArgumentsBase]:
        self._request_choose_charactor(action.player_idx)
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
    ) -> List[EventArgumentsBase]:
        if self.state != MatchState.PLAYER_ACTION_START:
            raise AssertionError(
                f'Cannot skip player action when match state is '
                f'{self.state}.'
            )
        self._set_match_state(MatchState.PLAYER_ACTION_REQUEST)
        logging.info(
            f'player {self.current_player} skipped player action.'
        )
        return []
