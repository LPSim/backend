from typing import Any, List, Literal

from ...struct import Cost

from ...action import MakeDamageAction

from ...event import SkillEndEventArguments

from ...consts import DamageElementalType, DamageType, SkillType

from ...modifiable_values import DamageDecreaseValue, DamageValue
from .base import ShieldTeamStatus


class FullPlate(ShieldTeamStatus):
    name: Literal['Full Plate'] = 'Full Plate'
    desc: str = (
        'Grants 2 Shield points to your active character. Before this Shield '
        'is fully consumed, the Physical DMG you take is halved. '
        '(The figure will be rounded up)'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2

    def value_modifier_DAMAGE_MULTIPLY(
            self, value: DamageDecreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageDecreaseValue:
        """
        If this shield exists, decrease physical damage by half.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match,
        ):
            # not this charactor receive damage, not modify
            return value
        if value.damage_elemental_type != DamageElementalType.PHYSICAL:
            # not physical damage, not modify
            return value
        assert self.usage > 0
        value.damage = (value.damage + 1) // 2  # round up
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        if skill is a normal attack, and is used by our Noelle, and she has
        talent I Got Your Back, heal all our charactors for 1 HP.

        TODO: from description, HP heal is triggered by the shield, not talent.
        The difference is when Noelle uses normal attack, other team status 
        (e.g. Sparks 'n' Splash) triggers before the shield and removes this 
        shield, whether HP heal will be triggered.
        """
        if event.action.skill_type != SkillType.NORMAL_ATTACK:
            # not using normal attack
            return []
        if self.position.player_idx != event.action.position.player_idx:
            # not this player using skill
            return []
        table = match.player_tables[self.position.player_idx]
        charactor = table.get_active_charactor()
        if charactor.name != 'Noelle':
            # not Noelle
            return []
        if (
            charactor.talent is None
            or charactor.talent.name != 'I Got Your Back'
        ):
            # not Noelle with talent I Got Your Back
            return []
        # heal all charactors for 1 HP.
        ret: List[MakeDamageAction] = []
        for charactor in table.charactors:
            if charactor.is_alive:
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
                            cost = Cost(),
                        )
                    ],
                    charactor_change_rule = 'NONE',
                ))
        return ret


GeoTeamStatus = FullPlate | FullPlate