"""
Wrappers for gymnasium. If want to use pettingzoo, may need to modify them.
"""

import os  # noqa
from typing import Type
import numpy as np
from pettingzoo.utils.wrappers import BaseWrapper
from pettingzoo import AECEnv
import torch

from lpsim.agents.interaction_agent import InteractionAgent
from lpsim.env.env import LPSimBaseV0Env
from lpsim.env.utils import cost_default_selector
from lpsim.server.card.equipment.artifact.base import ArtifactBase
from lpsim.server.card.equipment.weapon.base import WeaponBase
from lpsim.server.card.support.base import SupportBase
from lpsim.server.character.character_base import CharacterBase, TalentBase
from lpsim.server.consts import CostLabels, ObjectType, WeaponType
from lpsim.server.deck import Deck
from lpsim.server.interaction import Requests
from lpsim.server.match import Match, MatchConfig
from lpsim.server.object_base import CardBase, ObjectBase
from lpsim.server.player_table import PlayerTable
from lpsim.server.status.team_status.base import TeamStatusBase
from lpsim.server.struct import Cost
from lpsim.server.summon.base import SummonBase
from lpsim.utils.desc_registry import get_desc_patch


class ArrayLikeObservationWrapper(BaseWrapper):
    """
    Convert dict observation to array-like observation.
    As length are not fixed (e.g. status), some part will have non-fixed length arries,
    may need to pad to same length with other wrappers.

    output will be a dict[str, np.array], str to describe type, and np.array to save
    values. For character status, use 'p0c1.status' as keys. Detailed array structure
    will be filled later.

    Additionally, round number is a np.ndarray scalar int, and requests contains all
    possible requests with their original type.

    To be able to pack variable length array, maximum possible request number and
    maximum status number can be set. For requests None are padded, and for status,
    all-zero are padded. As 0 is reserved in mapping id, models can distinguish such
    paddings.
    Other length limits are retrieved from match_config, i.e. hand size, deck size,
    summon & support number. TODO: after version 4.6, deck size may exceed original
    deck size. Need to support.
    """

    element_like_lists = [
        "NONE",
        "CRYO",
        "HYDRO",
        "PYRO",
        "ELECTRO",
        "GEO",
        "DENDRO",
        "ANEMO",
        "OMNI",
        "PHYSICAL",
        "PIERCING",
        "HEAL",
    ]

    weapon_type_lists = [
        WeaponType.CATALYST,
        WeaponType.BOW,
        WeaponType.CLAYMORE,
        WeaponType.POLEARM,
        WeaponType.SWORD,
        WeaponType.OTHER,
    ]

    def __init__(
        self,
        env: AECEnv,
        max_possible_action_number: int = 20,
        max_possible_status_number: int = 10,
    ):
        super().__init__(env)
        self.max_possilable_action_number: int = max_possible_action_number
        self.max_possible_status_number = max_possible_status_number
        inner_env: LPSimBaseV0Env = env.unwrapped  # type: ignore
        config = inner_env.match_config
        if config is None:
            config = MatchConfig()
        self._match_config = config
        self.max_possible_summon_number = self._match_config.max_summon_number
        self.max_possible_support_number = self._match_config.max_support_number
        self.max_possible_hand_number = self._match_config.max_hand_size
        max_possible_deck_number = self._match_config.card_number
        if max_possible_deck_number is None:
            max_possible_deck_number = 30
        self.max_possible_deck_number = max_possible_deck_number
        self._init_name_to_id_map()

        self.appear_names = set()

    @staticmethod
    def card_type(card: CardBase) -> int:
        if card.type == ObjectType.CARD:
            return 0
        elif card.type == ObjectType.WEAPON:
            return 1
        elif card.type == ObjectType.ARTIFACT:
            return 2
        elif card.type == ObjectType.TALENT:
            return 3
        elif card.type == ObjectType.SUPPORT:
            return 4
        elif card.type == ObjectType.ARCANE:
            return 5
        else:
            raise ValueError(f"Unknown type {card.type}")

    @staticmethod
    def _get_key(key, version):
        """
        cat with !, so smaller version will list before larger.
        """
        return f"{version}!{key}"

    @staticmethod
    def _to_one_hot(idx: int, tot: int, dtype: Type = int) -> np.ndarray:
        arr = np.zeros(tot, dtype=dtype)
        arr[idx] = 1
        return arr

    @staticmethod
    def _retrieve_attr(obj: ObjectBase, key: str, default: float = -1) -> float:
        """
        Retrieve attribute from obj. If attr not exist, return default.
        """
        if hasattr(obj, key):
            return getattr(obj, key)
        return default

    def _init_name_to_id_map(self):
        """
        Do mapping based on keys and versions. It will read from descs, generate all
        version|key pairs, sort them, and use their indices as the id. When new version
        is implemented, as version should increase, after sort they will be but at end
        of list and should not change ids of early ones. However, this may not
        consistent for all situations, and is highly recommended not using models
        trained on older versions and evaluating on newer versions directly.
        """
        self._name_to_id_map = {}
        full_name_version_list = ["0.0!INVALID"]  # 0 reserved as special key
        patch = get_desc_patch()
        for key, value in patch.items():
            assert "descs" in value
            versions = value["descs"].keys()
            for version in versions:
                full_name_version_list.append(self._get_key(key, version))
        full_name_version_list.sort()
        for idx, key in enumerate(full_name_version_list):
            self._name_to_id_map[key] = idx

    def name_to_id(self, obj: ObjectBase):
        type = obj.type
        if type == ObjectType.TALENT:
            assert isinstance(obj, TalentBase)
            desc_type: str = f"TALENT_{obj.character_name}"
        else:
            desc_type: str = type.value
        key = f"{desc_type}/{obj.name}"
        id = self._name_to_id_map[self._get_key(key, obj.version)]  # type: ignore
        self.appear_names.add(f"{key}|{id}")
        return id

    @classmethod
    def element_id(cls, element_like: str):
        """
        Consider multiple element types, including Element, DamegeElement, DieColor
        """
        assert element_like in cls.element_like_lists, f"{element_like} not in lists"
        return cls.element_like_lists.index(element_like)

    def reset(self, *argv, **kwargs):
        super().reset(*argv, **kwargs)
        # fname = f"logs/{os.getpid()}.txt"
        # with open(fname, 'a') as f:
        #     f.write('\n'.join(self.appear_names) + '\n')

    def team_status_observation(
        self, player_idx: int, team_status: list[TeamStatusBase]
    ) -> dict[str, np.ndarray]:
        """
        For each team status, it uses its id, usage, usage_this_round, limited_usage,
        counter as observation. If latter ones not exist, use -1 as placeholder.
        """
        result = []
        for order, a in enumerate(team_status):
            status_arr = [
                self.name_to_id(a),
                order,
                self._retrieve_attr(a, "usage"),
                self._retrieve_attr(a, "usage_this_round"),
                self._retrieve_attr(a, "limited_usage"),
                self._retrieve_attr(a, "counter"),
            ]
            result.append(status_arr)
        assert len(result) <= self.max_possible_status_number
        result += [[0] * 6] * (self.max_possible_status_number - len(result))
        result = np.array(result, dtype=float)
        return {f"p{player_idx}.team_status": result}

    def character_status_observation(
        self, character: CharacterBase
    ) -> dict[str, np.ndarray]:
        """
        For each character status, (including equipment), it uses its id, usage,
        usage_this_round, limited_usage, counter, and one-hot array with length 3
        as observation. If attributes not exist, use -1 as placeholder. For character
        status, one-hot is all zero; if is equipment, it represents the equip type.
        """
        attaches = character.attaches
        result = []
        for order, a in enumerate(attaches):
            attach_arr = [
                self.name_to_id(a),
                order,
                self._retrieve_attr(a, "usage"),
                self._retrieve_attr(a, "usage_this_round"),
                self._retrieve_attr(a, "limited_usage"),
                self._retrieve_attr(a, "counter"),
                isinstance(a, WeaponBase),
                isinstance(a, ArtifactBase),
                isinstance(a, TalentBase),
            ]
            result.append(attach_arr)
        assert len(result) <= self.max_possible_status_number
        result += [[0] * 9] * (self.max_possible_status_number - len(result))
        result = np.array(result, dtype=float)
        code = f"p{character.position.player_idx}c{character.position.character_idx}"
        return {f"{code}.status": result}

    def character_observation(
        self, character: CharacterBase, active_relative: int
    ) -> dict[str, np.ndarray]:
        """
        Observation a character.  It does not consider status of the character, only
        record information direct rely on the character.
        It considers hp, max_hp, damage_taken, charge, max_charge, is_alive,
        its element, its element application, its weapon type.
        Specifically, active_relative marks the relative position of the character
        relative to current active character. If self is active it is 0, and next is 1,
        next is 2...
        """
        # base data
        character_arr = np.array(
            [
                self.name_to_id(character),
                active_relative,
                character.hp,
                character.max_hp,
                character.damage_taken,
                character.charge,
                character.max_charge,
                character.is_alive,
            ],
            dtype=float,
        )

        # character element type
        character_ele = self._to_one_hot(
            self.element_id(character.element.value), 8, float
        )

        # element application
        character_app = np.zeros(8, dtype=float)
        for e in character.element_application:
            character_app[self.element_id(e.value)] = 1

        # weapon type
        character_weapon = self._to_one_hot(
            self.weapon_type_lists.index(character.weapon_type),
            len(self.weapon_type_lists),
            float,
        )

        # character active relative position. 4 is hardcode, 0, 1, 2, -1 ( = 3)
        character_arel = self._to_one_hot(active_relative, 4, float)

        character_arr = np.concatenate(
            (
                character_arr,
                character_ele,
                character_app,
                character_weapon,
                character_arel,
            )
        )
        code = f"p{character.position.player_idx}c{character.position.character_idx}"
        result = {code: character_arr}
        result.update(self.character_status_observation(character))
        return result

    def summon_observation(
        self, player_idx: int, summons: list[SummonBase]
    ) -> dict[str, np.ndarray]:
        """
        For each summon, it uses its id, usage, and element id
        as observation. If usage not exist, use -1 as placeholder.
        """
        result = []
        for idx, summon in enumerate(summons):
            result.append(
                [
                    idx,
                    self.name_to_id(summon),
                    self.element_id(summon.damage_elemental_type.value),
                    summon.usage if hasattr(summon, "usage") else -1,
                ]
            )
        assert len(result) <= self.max_possible_summon_number
        result += [[0] * 4] * (self.max_possible_summon_number - len(result))
        result = np.array(result, dtype=float)
        return {f"p{player_idx}.summon": result}

    @staticmethod
    def support_type(support: SupportBase) -> int:
        # location=0, companion=1, item=2
        if support.cost.label & CostLabels.LOCATION.value:
            return 0
        if support.cost.label & CostLabels.COMPANION.value:
            return 1
        if support.cost.label & CostLabels.ITEM.value:
            return 2
        raise AssertionError("unknown support type")

    def support_observation(
        self, player_idx: int, supports: list[SupportBase]
    ) -> dict[str, np.ndarray]:
        """
        For each support, it uses its id, usage, and support type
        as observation. If usage not exist, use -1 as placeholder.
        """
        result = []
        for idx, support in enumerate(supports):
            result.append(
                [
                    idx,
                    self.name_to_id(support),
                    self.support_type(support),
                    support.usage if hasattr(support, "usage") else -1,
                ]
            )
        assert len(result) <= self.max_possible_support_number
        result += [[0] * 4] * (self.max_possible_support_number - len(result))
        result = np.array(result, dtype=float)
        return {f"p{player_idx}.summon": result}

    def cost_observation(self, cost: Cost) -> np.ndarray:
        """
        one-hot ele type, ele number, same number, any number, charge. If no ele number,
        ele type is all zero.
        """
        if cost.elemental_dice_color is None:
            ele_type = np.zeros(9, dtype=int)
        else:
            # NONE and OMNI considered. they should be always 0, but not really matter
            ele_type = self._to_one_hot(self.element_id(cost.elemental_dice_color), 9)
        return np.concatenate(
            (
                ele_type,
                np.array(
                    [
                        cost.elemental_dice_number,
                        cost.same_dice_number,
                        cost.any_dice_number,
                        cost.charge,
                    ]
                ),
            )
        )

    def card_observation(self, card: CardBase, cost: Cost | None = None) -> np.ndarray:
        """
        For one card, it uses card id, card type, card original cost and card real cost
        cost as observation. cost is derived by cost_observation.

        If cost is not given, use card.cost as both costs; otherwise, use corresponding
        cost to create real cost and original cost.
        """
        result = np.array(
            [
                self.name_to_id(card),
                self.card_type(card),
            ],
            dtype=float,
        )
        if cost is None:
            real_cost = original_cost = card.cost
        else:
            real_cost = cost
            original_cost = cost.original_value
        assert isinstance(original_cost, Cost)
        return np.concatenate(
            [
                result,
                self.cost_observation(original_cost),
                self.cost_observation(real_cost),
            ]
        )

    def hand_observation(
        self, player_idx: int, hands: list[CardBase], requests: list[Requests]
    ) -> dict[str, np.ndarray]:
        """
        For each hand card, it will use card_observation to get observation. When
        requests is provided, it will find UseCardRequest, and pass to card_observation.
        """
        target_requests: dict[int, Cost | None] = {
            idx: None for idx in range(len(hands))
        }
        for req in requests:
            if req.player_idx == player_idx and req.name == "UseCardRequest":
                target_requests[req.card_idx] = req.cost
        result = [
            self.card_observation(x, target_requests[idx])
            for idx, x in enumerate(hands)
        ]
        assert len(result) <= self.max_possible_hand_number
        result += [np.zeros((28))] * (self.max_possible_hand_number - len(result))
        result = np.stack(result, dtype=float)
        return {f"p{player_idx}.hand": result}

    def deck_observation(
        self, player_idx: int, decks: list[CardBase]
    ) -> dict[str, np.ndarray]:
        """
        deck card performs similar to hand cards, the only difference is that it will
        not contain real cost (as it cannot be played with dice costs), and is replaced
        by adding original cost twice.
        """
        result = [self.card_observation(x) for x in decks]
        assert len(result) <= self.max_possible_deck_number
        result += [np.zeros((28))] * (self.max_possible_deck_number - len(result))
        result = np.stack(result, dtype=float)
        return {f"p{player_idx}.deck": result}

    def grave_observation(self, player_idx: int):
        raise NotImplementedError()

    def player_deck_info_observation(self, deck: Deck) -> dict[str, np.ndarray]:
        raise NotImplementedError()

    def table_observation(
        self, player_idx: int, table: PlayerTable, is_current_player: bool
    ) -> dict[str, np.ndarray]:
        """
        Return player table information. It contains current dice, total dice number,
        hand number, deck number, alive character number, active character idx, is
        ended, is current player. Detailed information on table will be generated by
        corresponding observations.
        """
        die_observation = [0] * 9
        for c in table.dice.colors:
            die_observation[self.element_id(c.value)] += 1
        result = [
            *die_observation,
            sum(die_observation),
            len(table.hands),
            len(table.table_deck),
            sum([c.is_alive for c in table.characters]),
            table.active_character_idx,
            table.has_round_ended,
            is_current_player,
        ]
        result = np.array(result, dtype=float)
        if len(result) == 0:
            result = result.reshape(0, 16)
        return {f"p{player_idx}.table": np.array(result)}

    def player_observation(
        self,
        player_idx: int,
        table: PlayerTable,
        requests: list[Requests],
        is_current_player: bool,
    ) -> dict[str, np.ndarray]:
        """
        Gather and return all observation for one player side, based on above
        observation functions.
        """
        result_dict = {}
        result_dict.update(self.table_observation(player_idx, table, is_current_player))
        result_dict.update(self.hand_observation(player_idx, table.hands, requests))
        result_dict.update(self.deck_observation(player_idx, table.table_deck))
        result_dict.update(self.summon_observation(player_idx, table.summons))
        result_dict.update(self.support_observation(player_idx, table.supports))
        result_dict.update(self.team_status_observation(player_idx, table.team_status))
        assert len(table.characters) == 3, "only support 3 character"
        for idx, c in enumerate(table.characters):
            arel = idx - table.active_character_idx
            while arel < 0:
                arel += len(table.characters)
            if table.active_character_idx == -1:
                arel = -1  # TODO when -1, how to represent? all zero?
            result_dict.update(self.character_observation(c, arel))
            result_dict.update(self.character_status_observation(c))
        return result_dict

    def full_observation(self, match: Match) -> dict[str, np.ndarray]:
        """
        Full observation. It contains two player_observation, and round.
        """
        return {
            **self.player_observation(
                0, match.player_tables[0], match.requests, match.current_player == 0
            ),
            **self.player_observation(
                1, match.player_tables[1], match.requests, match.current_player == 1
            ),
            "round": np.array(match.round_number),
        }

    def observe(self, agent_id: int):
        match = super().observe(agent_id)
        assert match is not None
        obs = self.full_observation(match)

        # add requests into observation, pad to length 20 as maximum action number.
        # 10 cards, 4 skills, 2 switch character, tune, end.
        requests = match.requests[:]
        assert len(requests) <= self.max_possilable_action_number
        requests += [None] * (self.max_possilable_action_number - len(requests))
        obs["requests"] = requests
        return obs

        # TODO requests add to observation, another wrapper handle array-like response


class ArrayActionWrapper(BaseWrapper):
    """
    Accept array action to perform actions in requests. Action contains 4 numbers:
    1. player_idx: which player to response
    2. request_index: which request to perform
    3. request target: which target to select
    4. dice bits: which dice to use. if x & (1 << i) == 1, i-th die is used

    Some actions do not need to select target (e.g. round end), and value of request
    target will be ignored.

    Specifically, when request is switch_card, request target is ignored, and dice bits
    performs as hand cards bits.

    This wrapper will construct correct response (with the help of InteractionAgent).
    """

    def __init__(self, env: AECEnv):
        super().__init__(env)
        self._interact_agents = [
            InteractionAgent(player_idx=0, only_use_command=True),
            InteractionAgent(player_idx=1, only_use_command=True),
        ]
        self._req_name_to_command = {
            "SwitchCardRequest": "sw_card",
            "ChooseCharacterRequest": "choose",
            "RerollDiceRequest": "reroll",
            "SwitchCharacterRequest": "sw_char",
            "ElementalTuningRequest": "tune",
            "DeclareRoundEndRequest": "end",
            "UseSkillRequest": "skill",
            "UseCardRequest": "card",
        }

    def reset(self, seed: int | None = None, options: dict | None = None):
        return super().reset(seed, options)

    @staticmethod
    def _parse_idx_from_bits(dbits: int) -> list[int]:
        res = []
        now_idx = 0
        while dbits > 0:
            if dbits & 1 != 0:
                res.append(now_idx)
            now_idx += 1
            dbits //= 2
        return res

    def step(self, action: list[int]) -> None:
        assert len(action) == 4
        pidx, ridx, target, dbits = action
        didxs = self._parse_idx_from_bits(dbits)
        dstr = " ".join([str(x) for x in didxs])
        agent = self._interact_agents[pidx]
        req: Requests = self.observe(pidx)["requests"][ridx]  # type: ignore
        cmd = self._req_name_to_command[req.name]
        full_cmd = cmd

        # commands need source
        if cmd == "sw_char":
            full_cmd += f" {req.target_character_idx}"  # type: ignore
        elif cmd == "card":
            full_cmd += f" {req.card_idx}"  # type: ignore
        elif cmd == "skill":
            full_cmd += f" {req.skill_idx}"  # type: ignore

        # commands need target
        if cmd in ["choose", "card", "tune"]:
            full_cmd += f" {target}"

        # commands need dice / switch_card
        if cmd in ["sw_card", "reroll", "sw_char", "tune", "skill", "card"]:
            full_cmd += f" {dstr}"
        agent.commands = [full_cmd]
        inner_env: LPSimBaseV0Env = self.unwrapped  # type: ignore
        match = inner_env.match
        assert match is not None
        resp = agent.generate_response(match)
        return super().step(resp)


class AutoDiceWrapper(BaseWrapper):
    """
    Automatically select valid dice to perform an action.
    when action length is 3, create dice selection; otherwise, directly pass dice.
    TODO now only support all-omni status, and will not switch card at beginning.
    """

    def step(self, action: list[int]) -> None:
        if isinstance(action, torch.Tensor | np.ndarray):
            action = action.tolist()
        assert len(action) == 4 or len(action) == 3
        inner_env: LPSimBaseV0Env = self.unwrapped  # type: ignore
        if len(action) == 3:
            match = inner_env.match
            assert match is not None
            request = match.requests[action[1]]
            assert request.player_idx == action[0]
            if request.name in [
                "UseCardRequest",
                "UseSkillRequest",
                "SwitchCharacterRequest",
            ]:
                dice_idx = cost_default_selector(
                    match,
                    action[0],
                    "cost",
                    request.cost,  # type: ignore
                )
            elif request.name == "ElementalTuningRequest":
                dice_idx = cost_default_selector(match, action[0], "tune")
            elif request.name == "RerollDiceRequest":
                dice_idx = cost_default_selector(match, action[0], "reroll")
            else:
                dice_idx = []
            dice = sum([1 << x for x in dice_idx])
            action = action + [dice]
        return super().step(action)
