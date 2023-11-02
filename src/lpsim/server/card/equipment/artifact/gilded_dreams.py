from typing import Any, List, Literal

from ....consts import DamageType, ElementalReactionType, ObjectPositionType

from ....action import Actions, DrawCardAction

from ....event import ReceiveDamageEventArguments

from ....struct import Cost
from .base import RoundEffectArtifactBase


class ShadowOfTheSandKing(RoundEffectArtifactBase):
    name: Literal['Shadow of the Sand King']
    desc: str = (
        'When played: Draw a card. '
        'When the character to which this card is attached is your active '
        'character, then when an opposing character takes elemental reacction '
        'DMG: Draw a card. (Once per Round)'
    )
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1

    def equip(self, match: Any) -> List[Actions]:
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 1,
                draw_if_filtered_not_enough = True
            )
        ]

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        When opponent charactor take elemental reaction, draw a card.
        """
        if (
            self.position.area != ObjectPositionType.CHARACTOR
            or self.position.player_idx 
            == event.final_damage.target_position.player_idx
            or event.final_damage.element_reaction
            == ElementalReactionType.NONE
            or event.final_damage.damage_type != DamageType.DAMAGE
            or self.usage <= 0
            or self.position.charactor_idx != match.player_tables[
                self.position.player_idx].active_charactor_idx
        ):
            # not equipped, not opponent charactor, or not elemental reaction, 
            # or not damage, or no usage, or self not active charactor
            return []
        # draw card
        self.usage -= 1
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


GildedDreamses = ShadowOfTheSandKing | ShadowOfTheSandKing
