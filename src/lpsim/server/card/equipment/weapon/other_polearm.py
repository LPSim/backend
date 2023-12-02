
from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....action import Actions, ChargeAction

from ....action import ChangeObjectUsageAction, CreateObjectAction
from ....event import (
    ChargeEventArguments, RoundPrepareEventArguments, SkillEndEventArguments
)

from ....modifiable_values import DamageIncreaseValue
from ....status.charactor_status.base import ShieldCharactorStatus
from ....status.team_status.base import ShieldTeamStatus

from ....consts import FactionType, ObjectPositionType, SkillType, WeaponType

from ....struct import Cost
from .base import RoundEffectWeaponBase, WeaponBase


class VortexVanquisher_3_7(RoundEffectWeaponBase):
    name: Literal['Vortex Vanquisher']
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.7'] = '3.7'
    weapon_type: WeaponType = WeaponType.POLEARM
    max_usage_per_round: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If self has shield, +1 damage.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not current charactor using skill
            return value
        # modify damage
        assert mode == 'REAL'
        value.damage += self.damage_increase
        # if have shield, increase one more
        have_shield = False
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if issubclass(type(status), ShieldTeamStatus):
                have_shield = True
        if not have_shield:
            # no shield team status, check charactor status
            charactor = match.player_tables[
                self.position.player_idx].charactors[
                    self.position.charactor_idx]
            for status in charactor.status:
                if issubclass(type(status), ShieldCharactorStatus):
                    have_shield = True
        if have_shield:
            value.damage += 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        if self charactor use elemental skill, check whether have
        shield team status. If so, add 1 usage. 
        """
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        if self.usage <= 0:
            # no usage
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self charactor use skill or not equipped
            return []
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if issubclass(type(status), ShieldTeamStatus):
                # find shield status, add 3 usage
                self.usage -= 1
                return [ChangeObjectUsageAction(
                    object_position = status.position,
                    change_usage = 1,
                )]
        return []


class LithicSpear_3_7(WeaponBase):
    name: Literal['Lithic Spear']
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.7'] = '3.7'
    weapon_type: WeaponType = WeaponType.POLEARM

    def generate_shield(self, count: int) -> List[Actions]:
        count = min(count, 3)
        if count > 0:
            return [CreateObjectAction(
                object_position = self.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_name = self.name,
                object_arguments = {
                    'usage': count,
                    'max_usage': count,
                }
            )]
        return []

    def equip(self, match: Any) -> List[Actions]:
        """
        Generate shield
        """
        count = 0
        for c in match.player_tables[self.position.player_idx].charactors:
            if FactionType.LIYUE in c.faction:
                count += 1
        return self.generate_shield(count)


class LithicSpear_3_3(LithicSpear_3_7):
    version: Literal['3.3']

    def equip(self, match: Any) -> List[Actions]:
        """
        Generate shield
        """
        count = 0
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.is_alive and FactionType.LIYUE in c.faction:
                count += 1
        return self.generate_shield(count)


class EngulfingLightning_3_7(RoundEffectWeaponBase):
    name: Literal['Engulfing Lightning']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: WeaponType = WeaponType.POLEARM
    max_usage_per_round: int = 1

    def _charge_one(self, match: Any) -> List[ChargeAction]:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.charge == 0 and self.usage > 0:
            self.usage -= 1
            return [ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = self.position.charactor_idx,
                charge = 1,
            )]
        return []

    def equip(self, match: Any) -> List[Actions]:
        return super().equip(match) + self._charge_one(match)

    def event_handler_CHARGE(
        self, event: ChargeEventArguments, match: Any
    ) -> List[ChargeAction]:
        return self._charge_one(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        ret = super().event_handler_ROUND_PREPARE(event, match)
        return ret + self._charge_one(match)


register_class(
    LithicSpear_3_7 | VortexVanquisher_3_7 | EngulfingLightning_3_7
    | LithicSpear_3_3
)
