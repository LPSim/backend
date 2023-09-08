from typing import Any, List, Literal

from ...event import (
    ChooseCharactorEventArguments, RoundPrepareEventArguments, 
    SwitchCharactorEventArguments
)

from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, ObjectPositionType, SkillType
)

from ...modifiable_values import DamageIncreaseValue, DamageValue

from ...action import MakeDamageAction
from .base import UsageTeamStatus


class Icicle(UsageTeamStatus):
    name: Literal['Icicle'] = 'Icicle'
    desc: str = '''After you switch characters: Deal 2 Cryo DMG. Usage(s): 3'''
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3

    def _attack(self, match: Any) -> List[MakeDamageAction]:
        """
        attack enemy active charactor
        """
        if self.usage <= 0:  # pragma: no cover
            # no usage
            return []
        self.usage -= 1
        active_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = active_charactor.position,
                    damage = 2,
                    damage_elemental_type = DamageElementalType.CRYO,
                    cost = Cost()
                )
            ]
        )]

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self switch charactor, perform attack
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        return self._attack(match)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self choose charactor (when ally defeated), perform attack
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        return self._attack(match)


class IcyQuill(UsageTeamStatus):
    name: Literal['Icy Quill'] = 'Icy Quill'
    desc: str = (
        'Your character deals 1 increased Cryo DMG '
        '(Includes the DMG triggered by Cryo-infused Swirl reactions)'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 3

    talent_usage: int = 0
    talent_max_usage: int = 0

    def renew(self, new_status: 'IcyQuill') -> None:
        super().renew(new_status)
        self.talent_max_usage = max(
            new_status.talent_max_usage, self.talent_max_usage)
        self.talent_usage = max(
            new_status.talent_usage, self.talent_usage)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ):
        """
        When in round prepare, reset talent usage
        """
        self.talent_usage = self.talent_max_usage
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If our charactor skill or summon deal corresponding elemental DMG, 
        increase DMG.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, do nothing
            return value
        if value.position.player_idx != self.position.player_idx:
            # not this player, do nothing
            return value
        if value.damage_elemental_type != DamageElementalType.CRYO:
            # not corresponding elemental DMG, do nothing
            return value
        if value.position.area != ObjectPositionType.SKILL:
            # not charactor, do nothing
            return value
        # increase DMG
        assert mode == 'REAL'
        value.damage += 1
        # decrease usage
        skill = match.get_object(value.position)
        if (
            skill.skill_type == SkillType.NORMAL_ATTACK 
            and self.talent_usage > 0
        ):
            # decrease talent usage first
            self.talent_usage -= 1
        else:
            self.usage -= 1
        return value


CryoTeamStatus = Icicle | IcyQuill
