from typing import Any, List, Literal

from ....consts import DamageType, ObjectPositionType

from ....action import Actions

from ....event import MakeDamageEventArguments

from ....modifiable_values import DamageIncreaseValue
from .base import ArtifactBase
from ....struct import Cost


class CrownOfWatatsumi(ArtifactBase):
    name: Literal['Crown of Watatsumi']
    desc: str = (
        'For every 3 HP of healing your characters receive, this card '
        'accumulates 1 Sea-Dyed Foam (maximum of 2). '
        'When this character deals DMG: Consume all Sea-Dyed Foam. DMG is '
        'increased by 1 for each Sea-Dyed Foam consumed.'
    )
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0
    max_usage: int = 2
    counter: int = 0

    def equip(self, match: Any) -> List[Actions]:
        self.usage = 0
        self.counter = 0
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self use damage skill
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += self.usage
        self.usage = 0
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If our player receives heal, add counter.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        for damage in event.damages:
            if (
                damage.final_damage.target_position.player_idx
                != self.position.player_idx
                or damage.final_damage.damage_type != DamageType.HEAL
            ):
                # target not self player, or not heal
                continue
            # increase counter by heal
            self.counter += damage.hp_after - damage.hp_before
            # self.counter += - damage.final_damage.damage
            self.usage += self.counter // 3
            self.counter = self.counter % 3
            if self.usage >= self.max_usage:
                # usage full
                self.counter = 0
                self.usage = self.max_usage
        return []


OceanHuedArtifacts = CrownOfWatatsumi | CrownOfWatatsumi
