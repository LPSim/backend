

from typing import Any, Literal, List

from ...consts import CostLabels, ElementType, PlayerActionLabels

from ...action import Actions, ChangeObjectUsageAction, RemoveObjectAction

from ...event import (
    CharactorDefeatedEventArguments, ActionEndEventArguments, 
    MoveObjectEventArguments, SkillEndEventArguments
)

from ...modifiable_values import (
    CombatActionValue, CostValue, DamageIncreaseValue
)
from .base import RoundTeamStatus, ShieldTeamStatus, UsageTeamStatus


class ChangingShifts(UsageTeamStatus):
    name: Literal['Changing Shifts'] = 'Changing Shifts'
    desc: str = (
        'The next time you perform "Switch Character": '
        'Spend 1 less Elemental Die.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        assert self.usage > 0
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # not self switch charactor, do nothing
            return value
        if not (value.cost.label & CostLabels.SWITCH_CHARACTOR.value):
            # not switch charactor, do nothing
            return value
        # decrease 1 any cost
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_SWITCH_CHARACTOR(
        self, event: ActionEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When switch charactor end, check whether to remove.
        """
        return self.check_should_remove()


class IHaventLostYet(RoundTeamStatus):
    name: Literal["I Haven't Lost Yet!"] = "I Haven't Lost Yet!"
    desc: str = '''You cannot play "I Haven't Lost Yet!" again this round.'''
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1


class WindAndFreedom(RoundTeamStatus):
    name: Literal['Wind and Freedom'] = 'Wind and Freedom'
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends. '
        'Usage(s): 1 '
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    activated: bool = False

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        """
        When an enemy charactor is defeated, mark activated.
        """
        if (self.position.player_idx != event.action.player_idx):
            # enemy defeated, mark activated.
            self.activated = True
        return []

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CombatActionValue:
        """
        When enemy charactor defeated, 
        """
        assert mode == 'REAL'
        if not self.activated:
            # not activated, do nothing
            return value
        assert self.usage > 0
        assert self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        )
        # combat action end from self, if combat action, change to quick.
        if value.do_combat_action:
            value.do_combat_action = False
            self.usage -= 1
        # else:
        #     # Mona + Kaeya may trigger
        return value

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When action end event, check whether to remove.
        """
        return self.check_should_remove()


class LeaveItToMe(UsageTeamStatus):
    name: Literal['Leave It to Me!']
    desc: str = (
        'The next time you perform "Switch Character": '
        'The switch will be considered a Fast Action instead of a '
        'Combat Action.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CombatActionValue:
        assert self.usage > 0
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # not self switch charactor, do nothing
            return value
        if value.action_label & PlayerActionLabels.SWITCH.value == 0:
            # not switch charactor, do nothing
            return value
        if not value.do_combat_action:
            # already quick action, do nothing
            return value
        # self switch charactor, change to quick action
        value.do_combat_action = False
        assert mode == 'REAL'
        self.usage -= 1
        return value

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When action end event, check whether to remove.
        """
        return self.check_should_remove()


class EnduringRock(RoundTeamStatus):
    """
    Made Geo damage is determined by the following:
    in value_modifier_DAMAGE_INCREASE, check whether it is caused by our 
    charactor and is Geo damage. If so, mark did_geo_attack.
    in event_handler_SKILL_END, check whether did_geo_attack is True. If so,
    trigger the following check. And regardless of the result, reset
    did_geo_attack to False.

    As DAMAGE_INCREASE with skill as source must have SKILL_END in the 
    following, it will not mix other Geo damage or other charactor's skills.

    TODO: with Sparks 'n' Splash
    """
    name: Literal[
        'Elemental Resonance: Enduring Rock'
    ] = 'Elemental Resonance: Enduring Rock'
    desc: str = (
        'During this round, after your character deals Geo DMG next time: '
        'Should there be any Combat Status on your side that provides Shield, '
        'grant one such Status with 3 Shield points.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    did_geo_attack: bool = False

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not our charactor use skill, do nothing
            return value
        if value.damage_elemental_type != ElementType.GEO:
            # not Geo damage, do nothing
            return value
        # our charactor use Geo damage skill, mark did_geo_attack
        self.did_geo_attack = True
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction | RemoveObjectAction]:
        """
        if self charactor use skill, and did geo attack, check whether have
        shield team status. If so, add 3 usage. Regardless of the result, reset
        did_geo_attack to False.
        """
        if not self.did_geo_attack:
            # not fit condition, do nothing
            return []
        # reset did_geo_attack
        self.did_geo_attack = False
        if (
            self.position.player_idx != event.action.position.player_idx
        ):  # pragma: no cover
            # not self charactor use skill, do nothing
            return []
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if issubclass(type(status), ShieldTeamStatus):
                # find shield status, add 3 usage
                self.usage -= 1
                return [ChangeObjectUsageAction(
                    object_position = status.position,
                    change_type = 'DELTA',
                    change_usage = 3,
                )] + self.check_should_remove()
        return list(self.check_should_remove())


class WhereIstheUnseenRazor(RoundTeamStatus):
    name: Literal['Where Is the Unseen Razor?'] = 'Where Is the Unseen Razor?'
    desc: str = (
        'During this Round, the next time you play a Weapon card: '
        'Spend 2 less Elemental Dice.'
    )
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        decrease weapons cost by 2
        """
        if not value.cost.label & CostLabels.WEAPON.value:
            # not weapon, do nothing
            return value
        # try decrease twice
        success = [value.cost.decrease_cost(None), 
                   value.cost.decrease_cost(None)]
        if True in success:  # pragma: no branch
            # decrease success at least once
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        As it triggers on equipping weapon,
        When move object end, check whether to remove.
        """
        return self.check_should_remove()


EventCardTeamStatus = (
    WindAndFreedom | ChangingShifts | IHaventLostYet | LeaveItToMe 
    | EnduringRock | WhereIstheUnseenRazor
)
