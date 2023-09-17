
from typing import Any, List, Literal

from ....action import Actions

from ....action import ChangeObjectUsageAction, CreateObjectAction
from ....event import SkillEndEventArguments

from ....modifiable_values import DamageIncreaseValue
from ....status.charactor_status.base import ShieldCharactorStatus
from ....status.team_status.base import ShieldTeamStatus

from ....consts import FactionType, ObjectPositionType, SkillType, WeaponType

from ....struct import Cost
from .base import RoundEffectWeaponBase, WeaponBase


class VortexVanquisher(RoundEffectWeaponBase):
    name: Literal['Vortex Vanquisher']
    desc: str = (
        'The character deals +1 DMG. When your active character is protected '
        'by a Shield Character Status or a Shield Combat Status, you deal +1 '
        'DMG. After the character uses an Elemental Skill: If you have a '
        'Combat Status that grants a Shield on your side, add 1 Shield point '
        'to that Combat Status. (Once per Round)'
    )
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
                    change_type = 'DELTA',
                    change_usage = 1,
                )]
        return []


class LithicSpear(WeaponBase):
    name: Literal['Lithic Spear']
    desc: str = (
        'The character deals +1 DMG. '
        'When played: For each party member from Liyue, grant 1 Shield point '
        'to the character to which this is attached. (Max 3 points)'
    )
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


Polearms = LithicSpear | VortexVanquisher
