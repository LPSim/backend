from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....consts import DamageElementalType, DamageType, ObjectPositionType

from ....action import Actions, MakeDamageAction

from ....event import MakeDamageEventArguments

from ....modifiable_values import DamageIncreaseValue, DamageValue
from .base import ArtifactBase
from ....struct import Cost


class CrownOfWatatsumi_4_1(ArtifactBase):
    name: Literal['Crown of Watatsumi']
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


class OceanHuedClam_4_2(CrownOfWatatsumi_4_1):
    name: Literal['Ocean-Hued Clam']
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(any_dice_number = 3)

    def equip(self, match: Any) -> List[Actions]:
        super().equip(match)
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        # heal self
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        target_position = charactor.position,
                        damage_type = DamageType.HEAL,
                        damage = -3,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = Cost()
                    )
                ]
            )
        ]


register_class(CrownOfWatatsumi_4_1 | OceanHuedClam_4_2)
