from typing import Any, List, Literal
from ...dice import Dice

from ...action import (
    Actions, CreateDiceAction, DrawCardAction, 
    GenerateRerollDiceRequestAction, MakeDamageAction, RemoveDiceAction, 
    RemoveObjectAction
)
from ...event import MoveObjectEventArguments
from ...modifiable_values import CostValue, DamageValue, RerollValue
from ...event import RoundEndEventArguments, RoundPrepareEventArguments

from ...struct import Cost
from ...consts import (
    ELEMENT_DEFAULT_ORDER, ELEMENT_TO_DIE_COLOR, CostLabels, 
    DamageElementalType, DamageType, DieColor, ObjectPositionType
)
from .base import RoundEffectSupportBase, SupportBase


class LocationBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.LOCATION.value


class RoundEffectLocationBase(RoundEffectSupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.LOCATION.value


class LiyueHarborWharf(LocationBase):
    name: Literal['Liyue Harbor Wharf']
    desc: str = '''End Phase: Draw 2 cards.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        When in round end, draw 2 cards, and check if should remove.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        self.usage -= 1
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 2,
                draw_if_filtered_not_enough = True
            ),
        ] + self.check_should_remove()


class KnightsOfFavoniusLibrary(LocationBase):
    name: Literal['Knights of Favonius Library']
    desc: str = (
        'When played: Select any Elemental Dice to reroll. '
        'Roll Phase: Gain another chance to reroll.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0

    def play(self, match: Any) -> List[GenerateRerollDiceRequestAction]:
        return [GenerateRerollDiceRequestAction(
            player_idx = self.position.player_idx,
            reroll_times = 1,
        )]

    def value_modifier_REROLL(
        self, value: RerollValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> RerollValue:
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if value.player_idx != self.position.player_idx:
            # not self player
            return value
        value.value += 1
        return value


class WangshuInn(LocationBase):
    name: Literal['Wangshu Inn']
    desc: str = (
        'End Phase: Heal the most injured character on standby for 2 HP.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If back charactor not full hp, heal 2 hp, and check if should remove.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        table = match.player_tables[self.position.player_idx]
        charactors = table.charactors
        active = table.active_charactor_idx
        charactor = None
        for cnum, c in enumerate(charactors):
            if cnum == active or c.is_defeated:
                # active or defeated, do nothing
                continue
            if charactor is None or c.damage_taken > charactor.damage_taken:
                charactor = c
        if charactor is None:
            # no charactor on standby, do nothing
            return []
        if charactor.damage_taken <= 0:
            # full hp, do nothing
            return []
        self.usage -= 1
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        )] + self.check_should_remove()


class FavoniusCathedral(LocationBase):
    name: Literal['Favonius Cathedral']
    desc: str = '''End Phase: Heal your active character for 2 HP.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If active charactor not full hp, heal 2 hp, and check if should remove.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if charactor.damage_taken <= 0:
            # full hp, do nothing
            return []
        self.usage -= 1
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        )] + self.check_should_remove()


class Tenshukaku(LocationBase):
    name: Literal['Tenshukaku']
    desc: str = (
        'When the Action Phase begins: If you have 5 different kinds of '
        'Elemental Die, create 1 Omni Element.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When in round prepare, if have 5 different kinds of elemental dice,
        create 1 omni element.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        colors = match.player_tables[self.position.player_idx].dice.colors
        omni_number = 0
        color_set = set()
        for color in colors:
            if color == DieColor.OMNI:
                omni_number += 1
            else:
                color_set.add(color)
        if len(color_set) + omni_number < 5:
            # not enough different kinds of elemental dice
            return []
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 1,
            color = DieColor.OMNI
        )]


class SangonomiyaShrine(LocationBase):
    name: Literal['Sangonomiya Shrine']
    desc: str = '''End Phase: Heal all your characters for 1 HP.'''
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If active charactor not full hp, heal 2 hp, and check if should remove.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        charactors = match.player_tables[self.position.player_idx].charactors
        ret: List[MakeDamageAction] = []
        for charactor in charactors:
            if charactor.is_defeated or charactor.damage_taken <= 0:
                # full hp or defeated, do nothing
                continue
            ret.append(MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -1,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = self.cost.copy()
                    )
                ],
            ))
        if len(ret) == 0:
            # no charactor to heal, do nothing
            return []
        self.usage -= 1
        return ret + self.check_should_remove()


class SumeruCity(RoundEffectLocationBase):
    name: Literal['Sumeru City']
    desc: str = (
        'When your character uses a Skill or equips a Talent: If you do not '
        'have more Elemental Dice than cards in your hand, spend 1 less '
        'Elemental Die. (Once per Round)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1

    def play(self, match: Any) -> List[Actions]:
        """
        When played, reset usage.
        """
        self.usage = 1
        return super().play(match)

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        When self charactor use skills or equip talents, and have usage,
        and have less or equal elemental dice than cards in hand, reduce cost.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return value
        if self.usage == 0:
            # no usage
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        label = (
            CostLabels.NORMAL_ATTACK.value | CostLabels.ELEMENTAL_SKILL.value
            | CostLabels.ELEMENTAL_BURST.value | CostLabels.TALENT.value
        )
        if value.cost.label & label == 0:
            # not skill or talent
            return value
        table = match.player_tables[self.position.player_idx]
        if len(table.dice.colors) > len(table.hands):
            # more elemental dice than cards in hand
            return value
        # reduce cost
        if value.cost.decrease_cost(value.cost.elemental_dice_color):
            # success
            if mode == 'REAL':
                self.usage -= 1
        return value


class Vanarana(LocationBase):
    name: Literal['Vanarana']
    desc: str = (
        'End Phase: Collect up to 2 unused Elemental Dice. '
        'When the Action Phase begins: Reclaim the dice you collected using '
        'this card.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost()
    usage: int = 0
    colors: List[DieColor] = []

    def play(self, match: Any) -> List[Actions]:
        self.usage = 0
        self.colors = []
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When in round prepare, give collected dice back.
        """
        assert self.usage == len(self.colors)
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        if self.usage == 0:
            # no dice, do nothing
            return []
        ret: List[CreateDiceAction] = []
        for color in self.colors:
            ret.append(CreateDiceAction(
                player_idx = self.position.player_idx,
                color = color,
                number = 1
            ))
        self.usage = 0
        self.colors = []
        return ret

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[RemoveDiceAction]:
        """
        When in round end, collect up to 2 unused elemental dice.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        assert self.usage == 0 and len(self.colors) == 0
        current_dice: Dice = match.player_tables[
            self.position.player_idx].dice
        current_dice_colors = current_dice.colors
        if len(current_dice_colors) == 0:
            # no dice, do nothing
            return []
        dice_map = {}
        for color in current_dice_colors:
            if color not in dice_map:
                dice_map[color] = 0
            dice_map[color] += 1
        # first try to gather two same element dice
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if (
                color in dice_map 
                and dice_map[color] >= 2
                and len(self.colors) < 2
            ):
                self.colors = [color, color]
        if len(self.colors) < 2:
            # if not enough, gather any two dice
            for element in ELEMENT_DEFAULT_ORDER:
                color = ELEMENT_TO_DIE_COLOR[element]
                if color in dice_map and len(self.colors) < 2:
                    self.colors.append(color)
        if len(self.colors) < 2:
            # if not enough, gather omni
            if DieColor.OMNI in dice_map:
                self.colors.append(DieColor.OMNI)
                if len(self.colors) < 2 and dice_map[DieColor.OMNI] >= 2:
                    self.colors.append(DieColor.OMNI)
        self.usage = len(self.colors)
        dice_idxs = current_dice.colors_to_idx(self.colors)
        return [RemoveDiceAction(
            player_idx = self.position.player_idx,
            dice_idxs = dice_idxs,
        )]


class GoldenHouse(LocationBase):
    name: Literal['Golden House']
    desc: str = (
        'When you play a Weapon card or an Artifact card with an original '
        'cost of at least 3: Spend 1 less Elemental Die. (Once per Round)'
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(same_dice_number = 0)
    usage: int = 2
    used_this_round: bool = False

    card_cost_label: int = CostLabels.WEAPON.value
    decrease_threshold: int = 3

    def play(self, match: Any) -> List[Actions]:
        self.used_this_round = False
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.used_this_round = False
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        if card label match and original cost greater than threshold, 
        reduce cost.
        """
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and value.position.player_idx == self.position.player_idx
            and value.cost.original_value.total_dice_cost
            >= self.decrease_threshold
            and value.cost.label & self.card_cost_label != 0
            and not self.used_this_round
        ):
            # area right, player right, cost label match, cost greater than
            # threshold, and not used this round
            if value.cost.decrease_cost(None):
                if mode == 'REAL':
                    self.usage -= 1
                    self.used_this_round = True
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        if self.usage == 0:
            # if usage is zero, it run out of usage, remove it
            return list(self.check_should_remove())
        # otherwise, do parent event handler
        return super().event_handler_MOVE_OBJECT(event, match)


Locations = (
    LiyueHarborWharf | KnightsOfFavoniusLibrary | WangshuInn 
    | FavoniusCathedral | Tenshukaku | SangonomiyaShrine | SumeruCity 
    | Vanarana | GoldenHouse
)
