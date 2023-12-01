from typing import Any, List, Literal

from ....utils.class_registry import register_base_class, register_class

from ...modifiable_values import CombatActionValue, CostValue


from ...action import (
    Actions, CreateDiceAction, DrawCardAction, RemoveObjectAction
)

from ...event import (
    PlayerActionStartEventArguments, ReceiveDamageEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments, 
    SwitchCharactorEventArguments, UseCardEventArguments
)

from ...struct import Cost
from ...consts import (
    CostLabels, DamageElementalType, DamageType, IconType, ObjectPositionType, 
    PlayerActionLabels
)
from .base import RoundEffectSupportBase, SupportBase


class ItemBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


register_base_class(ItemBase)


class RoundEffectItemBase(RoundEffectSupportBase, ItemBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


class ParametricTransformer_3_3(ItemBase):
    name: Literal['Parametric Transformer']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    usage: int = 0
    max_usage: int = 3
    create_dice_number: int = 3
    progress_got: bool = False
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[Actions]:
        """
        When anyone start action, reset progress_got.
        """
        self.progress_got = False
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If elemental damage, gain progress
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.final_damage.damage_type == DamageType.HEAL:
            # heal, do nothing
            return []
        if (
            event.final_damage.damage_elemental_type in [
                DamageElementalType.PHYSICAL, DamageElementalType.PIERCING,
                DamageElementalType.HEAL
            ]
        ):
            # physical or piercing or heal, do nothing
            return []
        # get progress
        self.progress_got = True
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        If progress got, increase usage. If usage receives max_usage, 
        remove self and create different dice.
        """
        if self.progress_got:
            self.usage += 1
        self.progress_got = False
        if self.usage == self.max_usage:
            # remove self and create different dice
            return [
                RemoveObjectAction(
                    object_position = self.position,
                ),
                CreateDiceAction(
                    player_idx = self.position.player_idx,
                    number = self.create_dice_number,
                    different = True
                )
            ]
        return []


class NRE_4_1(RoundEffectItemBase):
    name: Literal['NRE']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1

    def draw_food_card(self) -> DrawCardAction:
        return DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = False,
            whitelist_cost_labels = CostLabels.FOOD.value
        )

    def play(self, match: Any) -> List[Actions]:
        return [self.draw_food_card()]

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        if self.position.area == ObjectPositionType.SUPPORT:
            # on support area, do effect
            if self.usage <= 0:
                # usage is 0, do nothing
                return []
            if (
                event.action.card_position.player_idx 
                != self.position.player_idx
            ):
                # not our charactor use card, do nothing
                return []
            if event.card.cost.label & CostLabels.FOOD.value == 0:
                # not food card, do nothing
                return []
            # our use food card, draw new food card
            self.usage -= 1
            return [self.draw_food_card()]
        # otherwise, do normal response
        return super().event_handler_USE_CARD(event, match)


class NRE_3_3(NRE_4_1):
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)


class RedFeatherFan_3_7(RoundEffectItemBase):
    name: Literal['Red Feather Fan']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1
    switch_count: int = 0  # activate after first switch

    # when decrease cost, should consume usage regardless of whether fast
    # action success
    is_cost_decreased: bool = False

    def play(self, match: Any) -> List[Actions]:
        self.switch_count = 0
        self.is_cost_decreased = False
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.switch_count = 0
        self.is_cost_decreased = False
        return super().event_handler_ROUND_PREPARE(event, match)

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[Actions]:
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if self.position.player_idx != event.action.player_idx:
            # not our charactor switch, do nothing
            return []
        # activate
        self.switch_count += 1
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        if activated, and our switch charactor, try to decrease cost.
        if success, mark is_cost_decreased.
        """
        if (
            self.switch_count < 1  # for cost, ignore first switch
            or self.position.area != ObjectPositionType.SUPPORT
            or self.position.player_idx != value.position.player_idx
            or self.usage <= 0
            or value.cost.label & CostLabels.SWITCH_CHARACTOR.value == 0
        ):
            # not activated, or not equipped, or not our charactor, 
            # or no usage, or not switch charactor, do nothing
            return value
        # decrease cost
        if value.cost.decrease_cost(None):
            if mode == 'REAL':
                self.is_cost_decreased = True
        return value

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> CombatActionValue:
        """
        If activated, and our switch charactor, try to act as fast action.
        Then if change to fast or decrease cost, consume usage.
        """
        if (
            self.switch_count < 2  # for combat action, ignore first two switch
            or self.position.area != ObjectPositionType.SUPPORT
            or self.position.player_idx != value.position.player_idx
            or self.usage <= 0
            or value.action_label & PlayerActionLabels.SWITCH.value == 0
        ):
            # not activated, or not equipped, or not our charactor, 
            # or no usage, or not switch charactor, do nothing
            return value
        # change to fast action
        changed = False
        if value.do_combat_action:
            value.do_combat_action = False
            changed = True
        assert mode == 'REAL'
        # decrease usage
        if changed or self.is_cost_decreased:
            self.usage -= 1
        return value


class TreasureSeekingSeelie_3_7(ItemBase):
    name: Literal['Treasure-Seeking Seelie']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0
    max_usage: int = 3
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[RemoveObjectAction | DrawCardAction]:
        """
        If our charactor use any skill, increase usage, and if usage
        reaches max_usage, draw 3 cards and remove self.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            source_area = ObjectPositionType.SUPPORT,
            target_area = ObjectPositionType.SKILL
        ):
            # not on support area, or not our charactor use skill
            return []
        # add usage
        self.usage += 1
        if self.usage != self.max_usage:
            # not reach max usage, do nothing
            return []
        # reach max usage, draw 3 cards and remove self
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 3,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position
            )
        ]


register_class(
    ParametricTransformer_3_3 | NRE_4_1 | NRE_3_3 | RedFeatherFan_3_7 
    | TreasureSeekingSeelie_3_7
)
