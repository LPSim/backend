import logging

import numpy as np
from typing import Literal, List
from enum import Enum

from utils import BaseModel
from .deck import Deck
from .player_table import PlayerTable
from .action import (
    Actions, 
    DrawCardAction,
    RestoreCardAction,
    RemoveCardAction,
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
    DeclareRoundEndAction,
    CombatActionAction,
    SwitchCharactorAction,
)
from .registry import Registry, ObjectSortRule
from .interaction import (
    Requests, Responses, RequestActionType,
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    ElementalTuningRequest, ElementalTuningResponse,
    DeclareRoundEndRequest, DeclareRoundEndResponse,
)
from .consts import DieColor, ELEMENT_TO_DIE_COLOR
from .die import Die
from .event import (
    EventArguments,
    DrawCardEventArguments, 
    RestoreCardEventArguments, 
    RemoveCardEventArguments,
    ChooseCharactorEventArguments,
    CreateDiceEventArguments,
    RemoveDiceEventArguments,
    RoundPrepareEventArguments,
    DeclareRoundEndEventArguments,
    CombatActionEventArguments,
    SwitchCharactorEventArguments,
)
from .modifiable_values import (
    RerollValue, DiceCostValue,
)


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
        ROUND_START (str): A new round is starting.
        ROUND_ROLL_DICE (str): Waiting for players to re-roll dice.
        ROUND_PREPARING (str): Preparing phase starts.
        PLAYER_ACTION_START (str): Player action phase start.
        PLAYER_ACTION_REQUEST (str): Waiting for response from player.
        PLAYER_ACTION_ACT (str): After player has decided its action, the 
            action is being executed. Execution may be interrupted by requests,
            e.g. someone is knocked out, need to re-roll dice.
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

    ROUND_START = 'ROUND_START'
    ROUND_ROLL_DICE = 'ROUND_ROLL_DICE'
    ROUND_PREPARING = 'ROUND_PREPARING'

    PLAYER_ACTION_START = 'PLAYER_ACTION_START'
    PLAYER_ACTION_REQUEST = 'PLAYER_ACTION_REQUEST'
    PLAYER_ACTION_ACT = 'PLAYER_ACTION_ACT'

    ROUND_ENDING = 'ROUND_ENDING'
    ROUND_ENDED = 'ROUND_ENDED'

    ENDED = 'ENDED'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class MatchConfig(BaseModel):
    """
    """
    random_first_player: bool = True
    initial_hand_size: int = 5
    initial_card_draw: int = 2
    initial_dice_number: int = 8
    initial_dice_reroll_times: int = 1
    card_number: int = 30
    max_same_card_number: int = 2
    charactor_number: int = 3
    max_round_number: int = 15
    max_hand_size: int = 10
    max_dice_number: int = 16
    max_summon_number: int = 4
    max_support_number: int = 4

    def check_config(self) -> bool:
        """
        Check whether the config is legal.
        """
        if self.initial_hand_size > self.max_hand_size:
            logging.error('initial hand size should not be greater than '
                          'max hand size')
            return False
        if self.initial_card_draw > self.card_number:
            logging.error('initial card draw should not be greater than '
                          'card number')
            return False
        if self.initial_dice_number > self.max_dice_number:
            logging.error('initial dice number should not be greater than '
                          'max dice number')
            return False
        return True


class Match(BaseModel):
    """
    """

    name: Literal['Match'] = 'Match'

    match_config: MatchConfig = MatchConfig()

    # random state
    random_state: List = []
    _random_state: np.random.RandomState = np.random.RandomState()

    # match information
    round_number: int = 0
    current_player: int = -1
    player_tables: List[PlayerTable] = [PlayerTable(), PlayerTable()]
    match_state: MatchState = MatchState.WAITING
    action_queues: List[List[Actions]] = []
    requests: List[Requests] = []

    # registry, all objects on PlayerTable will be registered. it will update
    # on initialization, object creation and deletion, gives a unique id for 
    # the object, and collect event triggers of object.
    _registry: Registry = Registry()

    def __init__(self):
        super().__init__()
        if self.random_state:
            random_state = self.random_state[:]
            random_state[1] = np.array(random_state[1], dtype = 'uint32')
            self._random_state = np.random.RandomState(self.random_state)

    def set_deck(self, decks: List[Deck]):
        """
        Set the deck of the match.
        """
        if self.match_state != MatchState.WAITING:
            logging.error('Match is not in waiting state.')
            return
        assert len(decks) == len(self.player_tables)
        for player_table, deck in zip(self.player_tables, decks):
            player_table.player_deck_information = deck

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
        ret = self._random_state.random()
        self._save_random_state()
        return ret

    def _random_shuffle(self, array: List):
        """
        Shuffle the array based on random_state.
        """
        self._random_state.shuffle(array)
        self._save_random_state()

    def _set_match_state(self, new_state: MatchState):
        logging.info(f'Match state change from {self.match_state} to '
                     f'{new_state}.')
        self.match_state = new_state

    def _get_sort_rule(self) -> ObjectSortRule:
        """
        Return the sort rule of the match.
        """
        return ObjectSortRule(
            current_player_id = self.current_player,
            max_charactor_number = self.match_config.charactor_number,
            active_charactor_ids = [
                0 if table.active_charactor_id == -1 
                else table.active_charactor_id for table in self.player_tables
            ],
        )

    def start(self) -> bool:
        """
        Start a new match. MatchState should be WAITING. Check the config and
        start until reaching STARTING_CARD_SWITCH, then wait for responses 
        from player to switch cards.
        """
        if self.match_state != MatchState.WAITING:
            # TODO: support re-start
            # logging.error('Match is not waiting for start. If it is running '
            #               'or ended, please call stop first.')
            logging.error('Match is not waiting for start. If it is running '
                          'or ended, please re-generate a new match.')
            return False

        # make valid check
        if not self.match_config.check_config():
            logging.error('Match config is not valid.')
            self._set_match_state(MatchState.ERROR)
            return False
        if len(self.player_tables) != 2:
            logging.error('Only support 2 players now.')
            self._set_match_state(MatchState.ERROR)
            return False
        for pnum, player_table in enumerate(self.player_tables):
            is_legal = player_table.player_deck_information.check_legal(
                card_number = self.match_config.card_number,
                max_same_card_number = self.match_config.max_same_card_number,
                charactor_number = self.match_config.charactor_number
            )
            if not is_legal:
                logging.error(f'Player {pnum} deck is not legal.')
                self._set_match_state(MatchState.ERROR)
                return False

        self._set_match_state(MatchState.STARTING)

        # choose first player
        if self.match_config.random_first_player:
            self.current_player = int(self._random() > 0.5)
        else:
            self.current_player = 0

        # copy and randomize based on deck
        for pnum, player_table in enumerate(self.player_tables):
            # copy charactors
            for charactor in player_table.player_deck_information.charactors:
                charactor_copy = charactor.copy()
                charactor_copy.player_id = pnum
                self._registry.register(charactor_copy)
                player_table.charactors.append(charactor_copy)
            # copy cards
            for card in player_table.player_deck_information.cards:
                card_copy = card.copy()
                card_copy.player_id = pnum
                self._registry.register(card_copy)
                player_table.table_deck.append(card_copy)
            self._random_shuffle(player_table.table_deck)
            # add draw initial cards action
            event_args = self._act(DrawCardAction(
                object_id = -1,
                player_id = pnum, 
                number = self.match_config.initial_hand_size
            ))
            triggered_actions = self._registry.trigger_events(
                event_args, self._get_sort_rule())
            if triggered_actions:
                logging.error('Initial draw card should not trigger actions.')
                self._set_match_state(MatchState.ERROR)
                return False
        return True

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
            # check if it need response
            if len(self.requests) != 0:
                logging.info('There are still requests not responded.')
                return False
            # check if action is needed
            if len(self.action_queues) != 0:
                self._next_action()
                continue
            # all response and action are cleared, start state transition
            if self.match_state == MatchState.STARTING:
                self._set_match_state(MatchState.STARTING_CARD_SWITCH)
                self._request_switch_card()
            elif self.match_state == MatchState.STARTING_CARD_SWITCH:
                self._set_match_state(MatchState.STARTING_CHOOSE_CHARACTOR)
                self._request_choose_charactor()
            elif self.match_state == MatchState.STARTING_CHOOSE_CHARACTOR:
                self._set_match_state(MatchState.ROUND_START)
                self._round_start()
            elif self.match_state == MatchState.ROUND_ROLL_DICE:
                self._set_match_state(MatchState.ROUND_PREPARING)
                self._round_prepare()
            elif self.match_state == MatchState.ROUND_PREPARING:
                self._set_match_state(MatchState.PLAYER_ACTION_START)
                self._player_action_start()
            elif self.match_state == MatchState.PLAYER_ACTION_START:
                self._set_match_state(MatchState.PLAYER_ACTION_REQUEST)
                self._player_action_request()
            elif self.match_state == MatchState.PLAYER_ACTION_REQUEST:
                # request responded and all action clear
                self._player_action_end()
            elif self.match_state == MatchState.ROUND_ENDING:
                self._set_match_state(MatchState.ROUND_ENDED)
                self._round_ending()
            elif self.match_state == MatchState.ROUND_ENDED:
                self._set_match_state(MatchState.ROUND_START)
                self._round_start()
            else:
                raise NotImplementedError(
                    f'Match state {self.match_state} not implemented.')
            if len(self.requests) or not run_continuously:
                if len(self.requests):
                    logging.info(f'{len(self.requests)} requests generated.')
                return True

    def check_request_exist(self, request: Requests) -> bool:
        """
        Check if the request is valid.
        """
        for req in self.requests:
            if req == request:
                return True
        return False

    def respond(self, response: Responses) -> bool:
        """
        Deal with the response. After start, the match will simulate 
        until it needs response from player, and `self.requests` will have
        requests for all players. A player should choose all requests
        related to him and respond one of them. Different requests will use
        different respond function to deal with, and remove requests that do
        not need to respond or have responded. If all requests have been
        removed, call `self.step()` manually to continue simulation. 

        Returns:
            bool: True if success, False if error occurs.
        """
        logging.info(f'Response received: {response}')
        if len(self.requests) == 0:
            logging.error('Match is not waiting for response.')
            return False
        # check if the response is valid
        if not response.is_valid:
            logging.error('Response is not valid.')
            return False
        # check if the request exist
        if not self.check_request_exist(response.request):
            logging.error('Request does not exist.')
            return False
        # call different respond functions based on the type of response
        if isinstance(response, SwitchCharactorResponse):
            self._respond_switch_charactor(response)
        elif isinstance(response, ElementalTuningResponse):
            self._respond_elemental_tuning(response)
        elif isinstance(response, DeclareRoundEndResponse):
            self._respond_declare_round_end(response)
        # elif isinstance(response, UseSkillResponse):
        #     self._respond_use_skill(response)
        # elif isinstance(response, UseCardResponse):
        #     self._respond_use_card(response)
        elif isinstance(response, SwitchCardResponse):
            self._respond_switch_card(response)
        elif isinstance(response, ChooseCharactorResponse):
            self._respond_choose_charactor(response)
        elif isinstance(response, RerollDiceResponse):
            self._respond_reroll_dice(response)
        else:
            logging.error(f'Response type {type(response)} not recognized.')
            return False
        return True

    def _next_action(self):
        """
        Do one action in `self._action_queue`. It will pick the first action in
        the last action queue, do it, and trigger events. if events have
        triggered new actions, they will be added as a new action queue.
        """
        # pop empty action queue
        while len(self.action_queues):
            if len(self.action_queues[-1]) == 0:
                self.action_queues.pop()
            else:
                break
        # if no action queue remain, return
        if len(self.action_queues) == 0:
            return
        activated_action = self.action_queues[-1].pop(0)
        logging.info(f'Action activated: {activated_action}')
        event_args = self._act(activated_action)
        triggered_actions = self._registry.trigger_events(
            event_args, self._get_sort_rule())
        if triggered_actions:
            self.action_queues.append(triggered_actions)

    def _round_start(self):
        """
        Start a round. Will clear existing dice, generate new random dice
        and asking players to reroll dice.

        # TODO: implement locking dice colors like Jade Chamber.
        # TODO: send round start event.
        """
        for pnum, player_table in enumerate(self.player_tables):
            for dice in player_table.dice:
                self._registry.unregister(dice)
            player_table.dice.clear()
        # generate new dice
        event_args: List[EventArguments] = []
        for pnum, player_table in enumerate(self.player_tables):
            one_event_args = self._act(CreateDiceAction(
                object_id = -1,
                player_id = pnum,
                number = self.match_config.initial_dice_number,
                random = True
            ))
            event_args += one_event_args
        triggered_actions = self._registry.trigger_events(
            event_args, self._get_sort_rule())
        if len(triggered_actions) != 0:
            logging.error('Create dice should not trigger actions.')
            self._set_match_state(MatchState.ERROR)
            return False
        # collect actions triggered by round start
        # reroll dice chance. reroll times can be modified by objects.
        for pnum, player_table in enumerate(self.player_tables):
            reroll_times = self.match_config.initial_dice_reroll_times
            reroll_value = RerollValue(
                value = reroll_times,
                player_id = pnum,
            )
            self._registry.modify_value(
                reroll_value, 
                self._get_sort_rule(),
                mode = 'real',
            )
            self._request_reroll_dice(pnum, reroll_value.value)
        self._set_match_state(MatchState.ROUND_ROLL_DICE)

    def _round_prepare(self):
        """
        Activate round_prepare event, and add to actions.
        """
        event_arg = RoundPrepareEventArguments(
            player_go_first = self.current_player,
            round = self.round_number,
            dice_colors = [
                [dice.color for dice in table.dice]
                for table in self.player_tables
            ],
        )
        actions = self._registry.trigger_event(event_arg, 
                                               self._get_sort_rule())
        logging.info(f'In round prepare, {len(actions)} actions triggered.')
        self.action_queues.append(actions)

    def _player_action_start(self):
        """
        Start a player's action phase. Will generate action phase start event.  
        TODO generate event
        """
        not_all_declare_end = False
        for table in self.player_tables:
            if not table.has_round_ended:
                not_all_declare_end = True
                break
        if not not_all_declare_end:
            # all declare ended, go to round ending
            self._set_match_state(MatchState.ROUND_ENDING)
            return

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
        self._request_switch_charactor(self.current_player)
        self._request_elemental_tuning(self.current_player)
        self._request_declare_round_end(self.current_player)
        self._request_use_skill(self.current_player)
        self._request_use_card(self.current_player)

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
            self._set_match_state(MatchState.PLAYER_ACTION_START)

    def _round_ending(self):
        """
        End a round. Will send round end event, collect actions.
        """

    """
    Request functions. To generate specific requests.
    """

    def _request_switch_card(self):
        """
        Generate switch card requests.
        """
        for pnum, player_table in enumerate(self.player_tables):
            self.requests.append(SwitchCardRequest(
                player_id = pnum,
                card_names = [card.name for card in player_table.hands]
            ))

    def _request_choose_charactor(self):
        """
        Generate switch card requests.
        """
        for pnum, player_table in enumerate(self.player_tables):
            self.requests.append(ChooseCharactorRequest(
                player_id = pnum,
                available_charactor_ids = list(range(len(
                    player_table.charactors)))
            ))

    def _request_reroll_dice(self, player_id: int, reroll_number: int):
        player_table = self.player_tables[player_id]
        self.requests.append(RerollDiceRequest(
            player_id = player_id,
            colors = [dice.color for dice in player_table.dice],
            reroll_times = reroll_number
        ))

    def _request_switch_charactor(self, player_id: int):
        """
        Generate switch charactor requests.
        TODO: With Leave It to Me, it can be a quick action.
        """
        table = self.player_tables[player_id]
        dice_cost = DiceCostValue(same_dice_number = 1)
        self._registry.modify_value(dice_cost, self._get_sort_rule(), 
                                    mode = 'test')
        if not dice_cost.is_valid(
            dice_colors = [die.color for die in table.dice],
            strict = False,
        ):
            return
        candidate_charactor_ids = [
            x for x in range(len(table.charactors))
            if x != table.active_charactor_id 
            and not table.charactors[x].is_defeated
        ]
        if len(candidate_charactor_ids):
            self.requests.append(SwitchCharactorRequest(
                player_id = player_id,
                type = RequestActionType.COMBAT,  # TODO currently only combat
                active_charactor_id = table.active_charactor_id,
                candidate_charactor_ids = candidate_charactor_ids,
                dice_colors = [die.color for die in table.dice],
                cost = dice_cost,
            ))

    def _request_elemental_tuning(self, player_id: int):
        table = self.player_tables[player_id]
        target_color = ELEMENT_TO_DIE_COLOR[
            table.charactors[table.active_charactor_id].element
        ]
        available_dice_colors = [
            dice.color for dice in table.dice
            if dice.color != target_color and dice.color != DieColor.OMNI
        ]
        available_card_ids = list(range(len(table.hands)))
        if len(available_dice_colors) and len(available_card_ids):
            self.requests.append(ElementalTuningRequest(
                player_id = player_id,
                dice_colors = available_dice_colors,
                card_ids = available_card_ids
            ))

    def _request_declare_round_end(self, player_id: int):
        self.requests.append(DeclareRoundEndRequest(
            player_id = player_id
        ))

    def _request_use_skill(self, player_id: int):
        """
        table = self.player_tables[player_id]
        if table.charactors[table.active_charactor_id].skill:
            self.requests.append(UseSkillRequest(
                player_id = player_id
            ))
        """
        ...

    def _request_use_card(self, player_id: int):
        """
        table = self.player_tables[player_id]
        available_card_ids = list(range(len(table.hands)))
        if len(available_card_ids):
            self.requests.append(UseCardRequest(
                player_id = player_id,
                card_ids = available_card_ids
            ))
        """
        ...

    """
    Response functions. To deal with specific responses.
    """

    def _respond_switch_card(self, response: SwitchCardResponse):
        # restore cards
        card_names = response.card_names
        card_name_dict = {}
        for card_name in card_names:
            if card_name not in card_name_dict:
                card_name_dict[card_name] = 0
            card_name_dict[card_name] += 1
        card_hand_ids = []
        card_hand_names = [x.name for x in self.player_tables[
            response.player_id].hands]
        for card_name, count in card_name_dict.items():
            start_idx = -1
            for _ in range(count):
                next_idx = card_hand_names.index(card_name, start_idx + 1)
                card_hand_ids.append(next_idx)
                start_idx = next_idx
        event_args: List[EventArguments] = []
        event_args += self._act(RestoreCardAction(
            object_id = -1,
            player_id = response.player_id,
            card_ids = card_hand_ids
        ))
        event_args += self._act(
            DrawCardAction(
                object_id = -1,
                player_id = response.player_id,
                number = len(response.card_ids)
            )
        )
        triggered_actions = self._registry.trigger_events(
            event_args, self._get_sort_rule())
        if triggered_actions:
            logging.error('Initial switch card should not trigger '
                          'actions.')
            self._set_match_state(MatchState.ERROR)
            return
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_id != response.player_id
        ]

    def _respond_choose_charactor(self, response: ChooseCharactorResponse):
        event_args = self._act(
            ChooseCharactorAction.from_response(response)
        )
        triggered_actions = self._registry.trigger_events(
            event_args, self._get_sort_rule())
        if len(triggered_actions) > 0:
            if len(self.action_queues) != 0:
                # already has actions in queue, append new actions
                # TODO extend or stack?
                self.action_queues[0].extend(triggered_actions)
            else:
                # no actions in queue, append new actions
                self.action_queues.append(triggered_actions)
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_id != response.player_id
        ]

    def _respond_reroll_dice(self, response: RerollDiceResponse):
        """
        Deal with reroll dice response. If there are still reroll times left,
        keep request and only substrat reroll times. If there are no reroll
        times left, remove request.
        """
        event_args = self._action_remove_dice(RemoveDiceAction.from_response(
            response
        ))
        triggered_actions: List[Actions] = []
        for event_arg in event_args:
            actions = self._registry.trigger_event(
                event_arg, self._get_sort_rule())
            triggered_actions.extend(actions)
        if len(triggered_actions) > 0:
            logging.error('Removing dice in Reroll Dice should not trigger '
                          'actions.')
            self._set_match_state(MatchState.ERROR)
            return
        event_args = self._action_create_dice(CreateDiceAction(
            object_id = -1,
            player_id = response.player_id,
            number = len(response.reroll_dice_ids),
            random = True,
        ))
        for event_arg in event_args:
            actions = self._registry.trigger_event(
                event_arg, self._get_sort_rule())
            triggered_actions.extend(actions)
        if len(triggered_actions) > 0:
            if len(self.action_queues) != 0:
                # already has actions in queue, append new actions
                # TODO extend or stack?
                self.action_queues[0].extend(triggered_actions)
            else:
                # no actions in queue, append new actions
                self.action_queues.append(triggered_actions)
        # modify request
        for num, req in enumerate(self.requests):
            if isinstance(req, RerollDiceRequest):
                if req.player_id == response.player_id:
                    if req.reroll_times > 1:
                        req.reroll_times -= 1
                    else:
                        self.requests.pop(num)
                    break

    def _respond_switch_charactor(self, response: SwitchCharactorResponse):
        """
        Deal with switch charactor response. If it is combat action, add
        combat action to action queue. Remove related requests.
        """
        actions: List[Actions] = []
        cost_ids = response.cost_ids
        if len(cost_ids):
            actions.append(RemoveDiceAction(
                object_id = -1,
                player_id = response.player_id,
                dice_ids = cost_ids,
            ))
        self._registry.modify_value(
            value = response.request.cost.original_value,
            sort_rule = self._get_sort_rule(),
            mode = 'real'
        )  # TODO: should use original value. need test.
        actions.append(SwitchCharactorAction.from_response(response))
        if response.request.type == RequestActionType.COMBAT:
            actions.append(CombatActionAction(
                object_id = -1,
                player_id = response.player_id,
            ))
        self.action_queues.append(actions)
        self.requests = [x for x in self.requests
                         if x.player_id != response.player_id]

    def _respond_elemental_tuning(self, response: ElementalTuningResponse):
        """
        Deal with elemental tuning response. It is splitted into 3 actions,
        remove one hand card, remove one die, and add one die.
        """
        color = response.die_color
        table = self.player_tables[response.player_id]
        die_id = [die.color for die in table.dice].index(color)
        actions: List[Actions] = []
        actions.append(RemoveCardAction(
            object_id = -1,
            player_id = response.player_id,
            card_id = response.card_id,
            card_position = 'HAND',
            remove_type = 'BURNED'
        ))
        actions.append(RemoveDiceAction(
            object_id = -1,
            player_id = response.player_id,
            dice_ids = [die_id]
        ))
        actions.append(CreateDiceAction(
            object_id = -1,
            player_id = response.player_id,
            number = 1,
            color = ELEMENT_TO_DIE_COLOR[
                table.charactors[table.active_charactor_id].element]
        ))
        self.action_queues.append(actions)
        self.requests = [x for x in self.requests
                         if x.player_id != response.player_id]

    def _respond_declare_round_end(self, response: DeclareRoundEndResponse):
        """
        Deal with declare round end response. It is splitted into 2 actions,
        declare round end and combat action.
        """
        actions: List[Actions] = []
        actions.append(DeclareRoundEndAction.from_response(response))
        actions.append(CombatActionAction(
            object_id = -1,
            player_id = response.player_id,
        ))
        self.action_queues.append(actions)
        self.requests = [x for x in self.requests
                         if x.player_id != response.player_id]

    def _respond_use_skill(self, response: Responses):
        ...

    def _respond_use_card(self, response: Responses):
        ...

    """
    Action Functions
    """

    def _act(self, action: Actions) -> List[EventArguments]:
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
        elif isinstance(action, CombatActionAction):
            return list(self._action_combat_action(action))
        else:
            logging.error(f'Unknown action {action}.')
            self._set_match_state(MatchState.ERROR)
            return []

    def _action_draw_card(
            self, 
            action: DrawCardAction) -> List[DrawCardEventArguments]:
        """
        Draw cards from the deck, and return the argument of triggered events.
        TODO: Input have draw rule, e.g. NRE.
        TODO: maintain card type from DECK_CARD to HAND_CARD
        TODO: destroy card if maximum hand size is reached
        """
        player_id = action.player_id
        number = action.number
        table = self.player_tables[player_id]
        if len(table.table_deck) < number:
            number = len(table.table_deck)
        names = [x.name for x in table.table_deck[:number]]
        table.hands.extend(table.table_deck[:number])
        table.table_deck = table.table_deck[number:]
        logging.info(
            f'Draw card action, player {player_id}, number {number}, '
            f'cards {names}, '
            f'deck size {len(table.table_deck)}, hand size {len(table.hands)}'
        )
        event_arg = DrawCardEventArguments(
            action = action,
        )
        return [event_arg]

    def _action_restore_card(
            self, 
            action: RestoreCardAction) -> List[RestoreCardEventArguments]:
        """
        Restore cards to the deck.
        """
        player_id = action.player_id
        table = self.player_tables[player_id]
        card_ids = action.card_ids[:]
        card_ids.sort(reverse = True)  # reverse order to avoid index error
        card_names = [table.hands[cid].name for cid in card_ids]
        for cid in card_ids:
            table.table_deck.append(table.hands[cid])
            table.hands = table.hands[:cid] + table.hands[cid + 1:]
        logging.info(
            f'Restore card action, player {player_id}, number {len(card_ids)},'
            f' cards: {card_names}, '
            f'deck size {len(table.table_deck)}, hand size {len(table.hands)}'
        )
        event_arg = RestoreCardEventArguments(
            action = action,
            card_names = card_names
        )
        return [event_arg]

    def _action_remove_card(self, action: RemoveCardAction) \
            -> List[RemoveCardEventArguments]:
        player_id = action.player_id
        card_position = action.card_position
        remove_type = action.remove_type  # used or burned (Keqing, EleTuning)
        table = self.player_tables[player_id]
        if card_position == 'HAND':
            card = table.hands.pop(action.card_id)
            self._registry.unregister(card)
        elif card_position == 'DECK':
            card = table.table_deck.pop(action.card_id)
            self._registry.unregister(card)
        else:
            logging.error(f'Unknown card position {card_position}.')
            self._set_match_state(MatchState.ERROR)
            return []
        logging.info(
            f'Remove hand card action, player {player_id}, '
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
        Choose a charactor.
        """
        player_id = action.player_id
        charactor_id = action.charactor_id
        table = self.player_tables[player_id]
        logging.info(
            f'Choose charactor action, player {player_id}, '
            f'charactor id {charactor_id}, '
            f'name {table.charactors[charactor_id].name}'
        )
        original_charactor_id = table.active_charactor_id
        table.active_charactor_id = charactor_id
        event_arg = ChooseCharactorEventArguments(
            action = action,
            original_charactor_id = original_charactor_id
        )
        return [event_arg]

    def _action_create_dice(self, action: CreateDiceAction) \
            -> List[CreateDiceEventArguments]:
        """
        Create dice.
        """
        dice: List[Die] = []
        player_id = action.player_id
        table = self.player_tables[player_id]
        number = action.number
        color = action.color
        is_random = action.random
        is_different = action.different
        if is_random and is_different:
            logging.error('Dice cannot be both random and different.')
            self._set_match_state(MatchState.ERROR)
            return []
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
                dice.append(Die(color = selected_color))
        elif is_different:
            if number > len(candidates):
                logging.error('Not enough dice colors.')
                self._set_match_state(MatchState.ERROR)
                return []
            self._random_shuffle(candidates)
            candidates = candidates[:number]
            for selected_color in candidates:
                dice.append(Die(color = selected_color))
        else:
            if color is None:
                logging.error('Dice color should be specified.')
                self._set_match_state(MatchState.ERROR)
                return []
            for _ in range(number):
                dice.append(Die(color = color))
        # if there are more dice than the maximum, discard the rest
        max_obtainable_dice = (self.match_config.max_dice_number 
                               - len(table.dice))
        for die in dice[:max_obtainable_dice]:
            table.dice.append(die)
            self._registry.register(die)
        # sort dice by color
        table.sort_dice()
        logging.info(
            f'Create dice action, player {player_id}, '
            f'number {len(dice)}, '
            f'dice colors {[die.color for die in dice]}, '
            f'obtain {len(dice[:max_obtainable_dice])}, '
            f'over maximum {len(dice[max_obtainable_dice:])}, '
            f'current dice on table {table.dice}'
        )
        return [CreateDiceEventArguments(
            action = action,
            colors_generated = [die.color for die 
                                in dice[:max_obtainable_dice]],
            colors_over_maximum = [die.color for die 
                                   in dice[max_obtainable_dice:]]
        )]

    def _action_remove_dice(self, action: RemoveDiceAction) \
            -> List[RemoveDiceEventArguments]:
        player_id = action.player_id
        dice_ids = action.dice_ids
        table = self.player_tables[player_id]
        removed_dice: List[Die] = []
        dice_ids.sort(reverse = True)  # reverse order to avoid index error
        for idx in dice_ids:
            removed_dice.append(table.dice.pop(idx))
        for die in removed_dice:
            self._registry.unregister(die)
        # sort dice by color
        table.sort_dice()
        logging.info(
            f'Remove dice action, player {player_id}, '
            f'number {len(dice_ids)}, '
            f'dice colors {[die.color for die in removed_dice]}, '
            f'current dice on table {table.dice}'
        )
        return [RemoveDiceEventArguments(
            action = action,
            colors_removed = [die.color for die in removed_dice]
        )]

    def _action_declare_round_end(self, action: DeclareRoundEndAction) \
            -> List[DeclareRoundEndEventArguments]:
        player_id = action.player_id
        table = self.player_tables[player_id]
        logging.info(
            f'Declare round end action, player {player_id}.'
        )
        table.has_round_ended = True
        return [DeclareRoundEndEventArguments(
            action = action
        )]

    def _action_combat_action(self, action: CombatActionAction) \
            -> List[CombatActionEventArguments]:
        player_id = action.player_id
        if self.player_tables[1 - player_id].has_round_ended and \
                not self.player_tables[player_id].has_round_ended:
            # the other player has declared round end and current player not, 
            # do not change current player.
            pass
        else:
            # change current player. If no player has declared round end,
            # the current player will be changed to the other player.
            # Otherwise, two players all declared round end, the other player
            # goes first in the next round.
            self.current_player = 1 - player_id
        logging.info(
            f'player {player_id} did a combat action, current player '
            f'is {self.current_player}.'
        )
        return [CombatActionEventArguments(
            action = action
        )]

    def _action_switch_charactor(self, action: SwitchCharactorAction) \
            -> List[SwitchCharactorEventArguments]:
        player_id = action.player_id
        table = self.player_tables[player_id]
        current_active_id = table.active_charactor_id
        current_active_name = table.charactors[current_active_id].name
        charactor_id = action.charactor_id
        charactor_name = table.charactors[charactor_id].name
        logging.info(
            f'player {player_id} '
            f'from charactor {current_active_name}:{current_active_id} '
            f'switched to charactor {charactor_name}:{charactor_id}.'
        )
        table.active_charactor_id = charactor_id
        return [SwitchCharactorEventArguments(
            action = action,
            last_active_charactor_id = current_active_id,
        )]
