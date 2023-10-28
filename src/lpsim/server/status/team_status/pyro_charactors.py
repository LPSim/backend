from typing import Any, List, Literal

from ...struct import Cost

from ...modifiable_values import (
    DamageDecreaseValue, DamageIncreaseValue, DamageValue
)

from ...consts import (
    DamageElementalType, DamageType, IconType, ObjectPositionType, SkillType
)

from ...action import MakeDamageAction, RemoveObjectAction

from ...event import MakeDamageEventArguments, SkillEndEventArguments
from .base import (
    DefendTeamStatus, ExtraAttackTeamStatus, RoundTeamStatus, UsageTeamStatus
)


class SparksNSplash(UsageTeamStatus):
    name: Literal["Sparks 'n' Splash"] = "Sparks 'n' Splash"
    desc: str = (
        "After a character to which Sparks 'n' Splash is attached uses a "
        "Skill: Deals 2 Pyro DMG to their team's active character. Usage(s): 2"
    )
    version: Literal['3.4'] = '3.4'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When attached charactor use skill, then damage itself.
        """
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
            return [MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = self.position.player_idx,
                damage_value_list = [DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = active_charactor.position,
                    damage = 2,
                    damage_elemental_type = DamageElementalType.PYRO,
                    cost = Cost()
                )]
            )]
        else:
            return []  # pragma: no cover


class InspirationField(RoundTeamStatus):
    name: Literal['Inspiration Field'] = 'Inspiration Field'
    desc: str = (
        "When your character uses a Skill: If this character has at least 7 "
        "HP, deal +2 additional DMG for this instance. After the Skill DMG "
        "is finalized, if this character's HP is not greater than 6, heal "
        "this character for 2 HP."
    )
    buff_desc: str = (
        "When your character uses a Skill: If this character has at least 7 "
        "HP, deal +2 additional DMG for this instance. After the Skill DMG "
        "is finalized, heal this character for 2 HP."
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    talent_activated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = self.buff_desc

    def renew(self, new_status: 'InspirationField') -> None:
        super().renew(new_status)
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = self.buff_desc

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If charactor HP greater than 7, or talent activated, increase damage
        by 2
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not our charactor use skill, do nothing
            return value
        charactor = match.player_tables[value.position.player_idx].charactors[
            value.position.charactor_idx]
        if not self.talent_activated and charactor.hp < 7:
            # no talent and hp less than 7, do nothing
            return value
        # increase damage by 2
        value.damage += 2
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If our charactor use skill and HP less than 7, heal 2 HP
        """
        if self.position.player_idx != event.action.position.player_idx:
            # not our charactor, do nothing
            return []
        charactor = match.player_tables[
            event.action.position.player_idx].charactors[
                event.action.position.charactor_idx]
        if charactor.hp > 6:
            # HP greater than 6, do nothing
            return []
        # heal this charactor by 2
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                )
            ],
        )]


class AurousBlaze(RoundTeamStatus, ExtraAttackTeamStatus):
    name: Literal['Aurous Blaze'] = 'Aurous Blaze'
    desc: str = (
        'After your character other than Yoimiya uses a Skill: '
        'Deal 1 Pyro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    trigger_skill_type: SkillType | None = None
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    decrease_usage: bool = False

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        if skill used by self player but not yoimiya, make damage to opponent
        active charactor.
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if charactor.name == 'Yoimiya':
            # yoimiya use skill
            return []
        return super().event_handler_SKILL_END(event, match)


class Pyronado(UsageTeamStatus, ExtraAttackTeamStatus):
    name: Literal['Pyronado'] = 'Pyronado'
    desc: str = '''After your character uses a Skill: Deal 2 Pyro DMG.'''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    newly_created: bool = True
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    trigger_skill_type: SkillType | None = None
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    decrease_usage: bool = True

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If newly created, should not trigger immediately.
        """
        if self.newly_created:
            self.newly_created = False
            return []
        return super().event_handler_SKILL_END(event, match)


class FierySanctumField(DefendTeamStatus):
    name: Literal['Fiery Sanctum Field'] = 'Fiery Sanctum Field'
    desc: str = (
        'When Dehya is on standby on your '
        'side, then when your active character takes damage: Decrease DMG '
        'taken by 1, and if Dehya has at least 7 HP, deal 1 Piercing DMG to '
        'her (once per round).'
    )
    version: Literal['4.1'] = '4.1'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    decrease_usage_by_damage: bool = False
    remove_triggered: bool = False

    def _find_dehya(self, match: Any) -> int:
        """
        Find first alive and standby dehya. If not found, return -1.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        active_idx = match.player_tables[
            self.position.player_idx].active_charactor_idx
        for cidx, charactor in enumerate(charactors):
            if (
                charactor.name == 'Dehya'
                and charactor.is_alive
                and cidx != active_idx
            ):
                return cidx
        return -1

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageDecreaseValue:
        """
        Check if have alive dehya on standby, if not, no effect.
        """
        dehya_idx = self._find_dehya(match)
        if dehya_idx == -1:
            # not found dehya
            return value
        return super().value_modifier_DAMAGE_DECREASE(value, match, mode)

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If self.shield_triggered, then check whether need to deal 1 piercing
        damage to dehya.
        """
        ret: List[MakeDamageAction | RemoveObjectAction] = []
        if self.usage == 0:
            if self.remove_triggered:
                # has triggered remove, do nothing
                return []
            self.remove_triggered = True
            # check if should attack dehya
            dehya_idx = self._find_dehya(match)
            assert dehya_idx != -1
            dehya = match.player_tables[
                self.position.player_idx].charactors[dehya_idx]
            if (
                dehya.hp >= 7
                and dehya.is_alive
            ):
                # after shield triggered, dehya has at least 7 hp and alive,
                # make 1 piercing damage to dehya
                ret.append(MakeDamageAction(
                    source_player_idx = self.position.player_idx,
                    target_player_idx = self.position.player_idx,
                    damage_value_list = [
                        DamageValue(
                            position = self.position,
                            target_position = dehya.position,
                            damage = 1,
                            damage_type = DamageType.DAMAGE,
                            damage_elemental_type 
                            = DamageElementalType.PIERCING,
                            cost = Cost(),
                        )
                    ]
                ))
        return ret + super().event_handler_MAKE_DAMAGE(event, match)


PyroTeamStatus = (
    SparksNSplash | InspirationField | AurousBlaze | Pyronado 
    | FierySanctumField
)
