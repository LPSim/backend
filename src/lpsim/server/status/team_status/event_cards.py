

from typing import Any, Literal, List

from ....utils.class_registry import register_class

from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DamageType, DieColor, ElementType, 
    ElementalReactionType, IconType, ObjectPositionType, PlayerActionLabels
)

from ...action import (
    Actions, ChangeObjectUsageAction, CreateDiceAction, DrawCardAction, 
    MakeDamageAction, RemoveObjectAction, SwitchCharactorAction
)

from ...event import (
    CharactorDefeatedEventArguments, ActionEndEventArguments, 
    DeclareRoundEndEventArguments, 
    MakeDamageEventArguments, MoveObjectEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments
)

from ...modifiable_values import (
    CombatActionValue, CostValue, DamageIncreaseValue, DamageValue
)
from .base import (
    RoundTeamStatus, ShieldTeamStatus, TeamStatusBase, UsageTeamStatus
)


class ChangingShifts_3_3(UsageTeamStatus):
    name: Literal['Changing Shifts'] = 'Changing Shifts'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

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


class IHaventLostYet_4_0(RoundTeamStatus):
    name: Literal["I Haven't Lost Yet!"] = "I Haven't Lost Yet!"
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.DEBUFF] = IconType.DEBUFF


class FreshWindOfFreedom_4_1(RoundTeamStatus):
    name: Literal['Fresh Wind of Freedom'] = 'Fresh Wind of Freedom'
    version: Literal['4.1'] = '4.1'
    usage: int = 1
    max_usage: int = 1
    activated: bool = False
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

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


class LeaveItToMe_3_3(UsageTeamStatus):
    name: Literal['Leave It to Me!']
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

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


class EnduringRock_3_3(RoundTeamStatus):
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
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    did_geo_attack: bool = False
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

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
                    change_usage = 3,
                )] + self.check_should_remove()
        return list(self.check_should_remove())


class WhereIstheUnseenRazor_4_0(RoundTeamStatus):
    name: Literal['Where Is the Unseen Razor?'] = 'Where Is the Unseen Razor?'
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF
    decrease_target: int = CostLabels.WEAPON.value

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        decrease weapons cost by 2
        """
        if value.position.player_idx != self.position.player_idx:
            # not self charactor, do nothing
            return value
        if value.cost.label & self.decrease_target == 0:
            # not weapon, do nothing
            return value
        # try decrease twice
        success = [value.cost.decrease_cost(None), 
                   value.cost.decrease_cost(None)]
        if True in success:
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


class SprawlingGreenery_3_3(RoundTeamStatus):
    name: Literal[
        'Elemental Resonance: Sprawling Greenery'
    ] = 'Elemental Resonance: Sprawling Greenery'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If we trigger elemental reaction, add 2 damage.
        """
        if (
            self.position.player_idx != value.position.player_idx
            or self.position.player_idx == value.target_position.player_idx
        ):
            # not we attack or we attack ourself, do nothing
            return value
        if value.damage_type != DamageType.DAMAGE:  # pragma: no cover
            # not damage, do nothing
            return value
        if value.element_reaction == ElementalReactionType.NONE:
            # not elemental reaction, do nothing
            return value
        if self.usage <= 0:
            # no usage, do nothing
            return value
        # we trigger elemental reaction, add 2 damage
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += 2
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When make damage end, check whether to remove.
        """
        return self.check_should_remove()


class ReviveOnCooldown_3_7(RoundTeamStatus):
    name: Literal['Revive on cooldown'] = 'Revive on cooldown'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.FOOD] = IconType.FOOD


class StoneAndContracts_3_7(TeamStatusBase):
    name: Literal['Stone and Contracts']
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def event_handler_ROUND_PREPARE(
        self, event: Any, match: Any
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        When round prepare, create 3 omni element and remove self.
        """
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = DieColor.OMNI,
                number = 3,
            ),
            RemoveObjectAction(
                object_position = self.position,
            )
        ]


class AncientCourtyard_3_8(RoundTeamStatus):
    name: Literal['Ancient Courtyard']
    version: Literal['3.8'] = '3.8'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        decrease weapons or artifact cost by 2
        """
        if value.position.player_idx != self.position.player_idx:
            # not self charactor, do nothing
            return value
        if value.cost.label & (CostLabels.WEAPON.value 
                               | CostLabels.ARTIFACT.value) == 0:
            # not weapon or artifact, do nothing
            return value
        # try decrease twice
        success = [value.cost.decrease_cost(None), 
                   value.cost.decrease_cost(None)]
        if True in success:
            # decrease success at least once
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        As it triggers on equipping weapon or artifact,
        When move object end, check whether to remove.
        """
        return self.check_should_remove()


class FatuiAmbusher_3_7(UsageTeamStatus):
    name: Literal[
        'Fatui Ambusher: Cryo Cicin Mage',
        'Fatui Ambusher: Mirror Maiden',
        'Fatui Ambusher: Pyroslinger Bracer',
        'Fatui Ambusher: Electrohammer Vanguard'
    ]
    element: DamageElementalType = DamageElementalType.PIERCING
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    activated_this_round: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name == 'Fatui Ambusher: Cryo Cicin Mage':
            self.element = DamageElementalType.CRYO
        elif self.name == 'Fatui Ambusher: Mirror Maiden':
            self.element = DamageElementalType.HYDRO
        elif self.name == 'Fatui Ambusher: Pyroslinger Bracer':
            self.element = DamageElementalType.PYRO
        else:
            assert self.name == 'Fatui Ambusher: Electrohammer Vanguard'
            self.element = DamageElementalType.ELECTRO

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        reset activated_this_round
        """
        self.activated_this_round = False
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When attached charactor use skill, then damage itself.
        """
        if self.activated_this_round:
            # already activated, do nothing
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True, 
            target_area = ObjectPositionType.SKILL,
        ):
            # not charactor use skill, not modify
            return []
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if self.usage > 0:  # pragma: no branch
            self.usage -= 1
            self.activated_this_round = True
            return [MakeDamageAction(
                damage_value_list = [DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = active_charactor.position,
                    damage = 1,
                    damage_elemental_type = self.element,
                    cost = Cost()
                )]
            )]
        else:
            return []  # pragma: no cover


class RhythmOfTheGreatDream_3_8(UsageTeamStatus):
    name: Literal['Rhythm of the Great Dream']
    version: Literal['3.8'] = '3.8'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        decrease weapons or artifact cost by 1
        """
        if value.position.player_idx != self.position.player_idx:
            # not self charactor, do nothing
            return value
        if value.cost.label & (CostLabels.WEAPON.value 
                               | CostLabels.ARTIFACT.value) == 0:
            # not weapon or artifact, do nothing
            return value
        # try decrease once
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        As it triggers on equipping weapon or artifact,
        When move object end, check whether to remove.
        """
        return self.check_should_remove()


class WhenTheCraneReturned_3_3(UsageTeamStatus):
    name: Literal['When the Crane Returned']
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    decrease_usage_when_trigger: bool = True
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[SwitchCharactorAction]:
        """
        when our charactor used skill, switch to next charactor
        """
        if self.position.player_idx != event.action.position.player_idx:
            # not our charactor, do nothing
            return []
        if self.usage <= 0:  # pragma: no cover
            return []
        next_idx = match.player_tables[
            self.position.player_idx].next_charactor_idx()
        if next_idx is None:
            # no next charactor, do nothing
            return []
        if self.decrease_usage_when_trigger:
            self.usage -= 1
        return [SwitchCharactorAction(
            player_idx = self.position.player_idx,
            charactor_idx = next_idx,
        )]

    def event_handler_SWITCH_CHARACTOR(
        self, event: ActionEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When switch charactor end, check whether to remove.
        """
        return self.check_should_remove()


class WindAndFreedom_4_1(WhenTheCraneReturned_3_3, RoundTeamStatus):
    name: Literal['Wind and Freedom'] = 'Wind and Freedom'
    version: Literal['4.1'] = '4.1'
    decrease_usage_when_trigger: bool = False


class WindAndFreedom_3_7(FreshWindOfFreedom_4_1):
    name: Literal['Wind and Freedom'] = 'Wind and Freedom'
    version: Literal['3.7']


class Pankration_4_1(TeamStatusBase):
    name: Literal['Pankration!'] = 'Pankration!'
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost()
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    def event_handler_DECLARE_ROUND_END(
        self, event: DeclareRoundEndEventArguments, match: Any
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        When anyone declears round end, another draw 2 cards and remove self
        """
        return [
            DrawCardAction(
                player_idx = 1 - event.action.player_idx,
                number = 2,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position,
            )
        ]


class Lyresong_4_2(WhereIstheUnseenRazor_4_0):
    name: Literal['Lyresong'] = 'Lyresong'
    version: Literal['4.2'] = '4.2'
    decrease_target: int = CostLabels.ARTIFACT.value


register_class(
    FreshWindOfFreedom_4_1 | ChangingShifts_3_3 | IHaventLostYet_4_0 
    | LeaveItToMe_3_3 | EnduringRock_3_3 | WhereIstheUnseenRazor_4_0 
    | SprawlingGreenery_3_3 | ReviveOnCooldown_3_7 | StoneAndContracts_3_7 
    | AncientCourtyard_3_8 | FatuiAmbusher_3_7 | RhythmOfTheGreatDream_3_8 
    | WhenTheCraneReturned_3_3 | WindAndFreedom_4_1 | Pankration_4_1 
    | Lyresong_4_2 | WindAndFreedom_3_7
)
