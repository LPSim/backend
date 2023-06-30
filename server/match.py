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
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
)
from .registry import Registry, ObjectSortRule
from .interaction import (
    Requests, Responses, 
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
)
from .consts import DiceColor
from .dice import Dice
from .event import (
    DrawCardEventArguments, 
    RestoreCardEventArguments, 
    ChooseCharactorEventArguments,
    CreateDiceEventArguments,
    RemoveDiceEventArguments,
)
from .modifiable_values import (
    RerollValue, RerollValueArguments,
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
        PLAYER_ACTION_START (str): Player is deciding its action.
        PLAYER_ACTION_ACT (str): After player has decided its action, the 
            action is being executed. Execution may be interrupted by requests,
            e.g. someone is knocked out, or need to re-roll dice.
        ROUND_ENDING (str): Ending phase starts.
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
    PLAYER_ACTION_ACT = 'PLAYER_ACTION_ACT'

    ROUND_ENDING = 'ROUND_ENDING'

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
    action_queue: List[List[Actions]] = []
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
            front_charactor_ids = [
                0 if table.front_charactor_id == -1 
                else table.front_charactor_id for table in self.player_tables
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
            event_args = self._action_draw_card(DrawCardAction(
                object_id = -1,
                player_id = pnum, 
                number = self.match_config.initial_hand_size
            ))
            triggered_actions: List[Actions] = []
            for event_arg in event_args:
                actions = self._registry.trigger_event(
                    event_arg, self._get_sort_rule())
                triggered_actions.extend(actions)
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
            if len(self.action_queue) != 0:
                self._next_action()
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
                raise NotImplementedError()
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
        removed, it will call `self.step` to continue simulation.

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
        if self.match_state == MatchState.STARTING_CARD_SWITCH:
            if isinstance(response, SwitchCardResponse):
                self._respond_switch_card(response)
            else:
                logging.error('Match is waiting for switch card response.')
        elif self.match_state == MatchState.STARTING_CHOOSE_CHARACTOR:
            if isinstance(response, ChooseCharactorResponse):
                self._respond_choose_charactor(response)
            else:
                logging.error('Match is waiting for choose charactor '
                              'response.')
        elif self.match_state == MatchState.ROUND_ROLL_DICE:
            if isinstance(response, RerollDiceResponse):
                self._respond_reroll_dice(response)
            else:
                logging.error('Match is waiting for reroll dice response.')
        else:
            raise NotImplementedError(
                f'Response to match state {self.match_state} not implemented.'
            )

        return True

    def _next_action(self):
        ...

    def _round_start(self):
        """
        Start a round. Will clear existing dices, generate new random dices
        and asking players to reroll dices.
        """
        for pnum, player_table in enumerate(self.player_tables):
            for dice in player_table.dices:
                self._registry.unregister(dice)
            player_table.dices.clear()
        # generate new dices
        event_args = []
        for pnum, player_table in enumerate(self.player_tables):
            one_event_args = self._action_create_dice(CreateDiceAction(
                object_id = -1,
                player_id = pnum,
                dice_number = self.match_config.initial_dice_number,
                dice_random = True
            ))
            event_args += one_event_args
        triggered_actions: List[Actions] = []
        for event_arg in event_args:
            sort_rule = ObjectSortRule(
                current_player_id = self.current_player,
                max_charactor_number = self.match_config.charactor_number,
                front_charactor_ids = [
                    table.front_charactor_id for table in self.player_tables
                ],
            )
            actions = self._registry.trigger_event(event_arg, sort_rule)
            triggered_actions.extend(actions)
        if len(triggered_actions) != 0:
            logging.error('Create dice should not trigger actions.')
            self._set_match_state(MatchState.ERROR)
            return False
        # collect actions triggered by round start
        # default reroll dice chance
        for pnum, player_table in enumerate(self.player_tables):
            reroll_times = self.match_config.initial_dice_reroll_times
            reroll_value = RerollValue(value = reroll_times)
            self._registry.modify_value(
                reroll_value, 
                self._get_sort_rule(),
                RerollValueArguments(player_id = pnum),
            )
            self._request_reroll_dice(pnum, reroll_value.value)
        self._set_match_state(MatchState.ROUND_ROLL_DICE)

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
            dice_colors = [dice.color for dice in player_table.dices],
            reroll_times = reroll_number
        ))

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
            response.request.player_id].hands]
        for card_name, count in card_name_dict.items():
            start_idx = -1
            for _ in range(count):
                next_idx = card_hand_names.index(card_name, start_idx + 1)
                card_hand_ids.append(next_idx)
                start_idx = next_idx
        event_args = self._action_restore_card(RestoreCardAction(
            object_id = -1,
            player_id = response.request.player_id,
            card_ids = card_hand_ids
        ))
        event_args += self._action_draw_card(
            DrawCardAction(
                object_id = -1,
                player_id = response.request.player_id,
                number = len(response.card_ids)
            )
        )
        triggered_actions: List[Actions] = []
        for event_arg in event_args:
            actions = self._registry.trigger_event(
                event_arg, self._get_sort_rule())
            triggered_actions.extend(actions)
        if triggered_actions:
            logging.error('Initial switch card should not trigger '
                          'actions.')
            self._set_match_state(MatchState.ERROR)
            return
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_id != response.request.player_id
        ]

    def _respond_choose_charactor(self, response: ChooseCharactorResponse):
        event_args = self._action_choose_charactor(
            ChooseCharactorAction.from_response(response)
        )
        triggered_actions: List[Actions] = []
        for event_arg in event_args:
            actions = self._registry.trigger_event(
                event_arg, self._get_sort_rule())
            triggered_actions.extend(actions)
        if len(triggered_actions) > 0:
            if len(self.action_queue) != 0:
                # already has actions in queue, append new actions
                # TODO extend or stack?
                self.action_queue[0].extend(triggered_actions)
            else:
                # no actions in queue, append new actions
                self.action_queue.append(triggered_actions)
        # remove related requests
        self.requests = [
            req for req in self.requests
            if req.player_id != response.request.player_id
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
            logging.error('Removing dice in Reroll dice should not trigger '
                          'actions.')
            self._set_match_state(MatchState.ERROR)
            return
        event_args = self._action_create_dice(CreateDiceAction(
            object_id = -1,
            player_id = response.request.player_id,
            dice_number = len(response.reroll_dice_ids),
            dice_random = True,
        ))
        for event_arg in event_args:
            actions = self._registry.trigger_event(
                event_arg, self._get_sort_rule())
            triggered_actions.extend(actions)
        if len(triggered_actions) > 0:
            if len(self.action_queue) != 0:
                # already has actions in queue, append new actions
                # TODO extend or stack?
                self.action_queue[0].extend(triggered_actions)
            else:
                # no actions in queue, append new actions
                self.action_queue.append(triggered_actions)
        # modify request
        for num, req in enumerate(self.requests):
            if isinstance(req, RerollDiceRequest):
                if req.player_id == response.request.player_id:
                    if req.reroll_times > 1:
                        req.reroll_times -= 1
                    else:
                        self.requests.pop(num)
                    break

    """
    Action functions. An actions function takes Action as input, do 
    changes of the game table, and return a list of triggered events.
    """

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
        # all_card_names = [card.name for card in table.hands]
        # card_id = [all_card_names.index(card_name) for card_name in card_ids]
        # card_id.sort(reverse = True)  # reverse order to avoid index error
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
        original_charactor_id = table.front_charactor_id
        table.front_charactor_id = charactor_id
        event_arg = ChooseCharactorEventArguments(
            action = action,
            original_charactor_id = original_charactor_id
        )
        return [event_arg]

    def _action_create_dice(self, action: CreateDiceAction) \
            -> List[CreateDiceEventArguments]:
        """
        Create dices.
        """
        dices: List[Dice] = []
        player_id = action.player_id
        table = self.player_tables[player_id]
        number = action.dice_number
        color = action.dice_color
        is_random = action.dice_random
        is_different = action.dice_different
        if is_random and is_different:
            logging.error('Dice cannot be both random and different.')
            self._set_match_state(MatchState.ERROR)
            return []
        candidates: List[DiceColor] = [
            DiceColor.CRYO, DiceColor.PYRO, DiceColor.HYDRO, DiceColor.ELECTRO,
            DiceColor.GEO, DiceColor.DENDRO, DiceColor.ANEMO
        ]
        # generate dices based on color
        if is_random:
            candidates.append(DiceColor.OMNI)  # random, can be omni
            for _ in range(number):
                selected_color = candidates[int(self._random() 
                                                * len(candidates))]
                dices.append(Dice(color = selected_color))
        elif is_different:
            if number > len(candidates):
                logging.error('Not enough dice colors.')
                self._set_match_state(MatchState.ERROR)
                return []
            self._random_shuffle(candidates)
            candidates = candidates[:number]
            for selected_color in candidates:
                dices.append(Dice(color = selected_color))
        else:
            if color is None:
                logging.error('Dice color should be specified.')
                self._set_match_state(MatchState.ERROR)
                return []
            for _ in range(number):
                dices.append(Dice(color = color))
        # if there are more dices than the maximum, discard the rest
        max_obtainable_dices = (self.match_config.max_dice_number 
                                - len(table.dices))
        for dice in dices[:max_obtainable_dices]:
            table.dices.append(dice)
            self._registry.register(dice)
        # sort dices by color
        table.sort_dices()
        logging.info(
            f'Create dice action, player {player_id}, '
            f'number {len(dices)}, '
            f'dice colors {[dice.color for dice in dices]}, '
            f'obtain {len(dices[:max_obtainable_dices])}, '
            f'over maximum {len(dices[max_obtainable_dices:])}, '
            f'current dices on table {table.dices}'
        )
        return [CreateDiceEventArguments(
            action = action,
            dice_colors_generated = [dice.color for dice 
                                     in dices[:max_obtainable_dices]],
            dice_colors_over_maximum = [dice.color for dice 
                                        in dices[max_obtainable_dices:]]
        )]

    def _action_remove_dice(self, action: RemoveDiceAction) \
            -> List[RemoveDiceEventArguments]:
        player_id = action.player_id
        dice_ids = action.dice_ids
        table = self.player_tables[player_id]
        removed_dices: List[Dice] = []
        dice_ids.sort(reverse = True)  # reverse order to avoid index error
        for idx in dice_ids:
            removed_dices.append(table.dices.pop(idx))
        for dice in removed_dices:
            self._registry.unregister(dice)
        # sort dices by color
        table.sort_dices()
        logging.info(
            f'Remove dice action, player {player_id}, '
            f'number {len(dice_ids)}, '
            f'dice colors {[dice.color for dice in removed_dices]}, '
            f'current dices on table {table.dices}'
        )
        return [RemoveDiceEventArguments(
            action = action,
            dice_colors_removed = [dice.color for dice in removed_dices]
        )]
