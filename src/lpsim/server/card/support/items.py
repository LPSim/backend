from typing import Any, List, Literal


from ...action import (
    Actions, CreateDiceAction, DrawCardAction, RemoveObjectAction
)

from ...event import (
    PlayerActionStartEventArguments, ReceiveDamageEventArguments, 
    SkillEndEventArguments, UseCardEventArguments
)

from ...struct import Cost
from ...consts import CostLabels, DamageElementalType, ObjectPositionType
from .base import RoundEffectSupportBase, SupportBase


class ItemBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


class RoundEffectItemBase(RoundEffectSupportBase):
    name: str
    desc: str
    version: str
    cost: Cost
    max_usage_per_round: int 
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


class ParametricTransformer(ItemBase):
    name: Literal['Parametric Transformer']
    desc: str = (
        'When either side uses a Skill: If Elemental DMG was dealt this card '
        'gains 1 Qualitative Progress. When this card gains 3 Qualitative '
        'Progress, discard this card, then create 3 different Basic Elemental '
        'Dice.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    usage: int = 0
    max_usage: int = 3
    create_dice_number: int = 3
    progress_got: bool = False

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
        if event.final_damage.damage_type == 'HEAL':
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


class NRE(RoundEffectItemBase):
    name: Literal['NRE']
    desc: str = (
        'When played: Draw 1 Food Event Card from your deck. '
        'When you play a Food Event Card: Draw 1 Food Event Card from your '
        'deck. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
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


class TreasureSeekingSeelie(ItemBase):
    name: Literal['Treasure-Seeking Seelie']
    desc: str = (
        'Triggers automatically once per Round: This card gains 1 Pigeon. '
        'When this card gains 3 Pigeons, discard this card, then draw 1 card '
        'and create Genius Invokation TCG Omni Dice Omni Element x1.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0
    max_usage: int = 3

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


Items = ParametricTransformer | NRE | TreasureSeekingSeelie
