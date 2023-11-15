from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import (
    RoundPrepareEventArguments, SkillEndEventArguments
)

from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, IconType, ObjectPositionType, SkillType, 
    WeaponType
)

from ...modifiable_values import (
    DamageElementEnhanceValue, DamageIncreaseValue, DamageValue
)

from ...action import MakeDamageAction
from .base import (
    DefendTeamStatus, RoundTeamStatus, ShieldTeamStatus, 
    SwitchActionTeamStatus, UsageTeamStatus, ElementalInfusionTeamStatus
)


class Icicle_3_3(SwitchActionTeamStatus):
    name: Literal['Icicle'] = 'Icicle'
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def _action(self, match: Any) -> List[MakeDamageAction]:
        """
        attack enemy active charactor
        """
        active_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
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


class IcyQuill_3_7(UsageTeamStatus):
    name: Literal['Icy Quill'] = 'Icy Quill'
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 3
    icon_type: Literal[IconType.ATK_UP_ICE] = IconType.ATK_UP_ICE

    talent_usage: int = 0
    talent_max_usage: int = 0

    def renew(self, new_status: 'IcyQuill_3_7') -> None:
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
        if self.usage <= 0:
            # no usage, do nothing
            return value
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


class ChonghuasFrostField_3_3(ElementalInfusionTeamStatus, RoundTeamStatus):
    name: Literal["Chonghua's Frost Field"] = "Chonghua's Frost Field"
    desc: Literal['', 'talent'] = ''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    talent_activated: bool = False

    infused_elemental_type: DamageElementalType = DamageElementalType.CRYO

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.talent_activated:
            self.desc = 'talent'

    def renew(self, object: 'ChonghuasFrostField_3_3'):
        super().renew(object)
        self.talent_activated = object.talent_activated
        if self.talent_activated:
            self.desc = 'talent'

    def charactor_is_using_right_weapon(
        self, match: Any, position: ObjectPosition
    ) -> bool:
        """
        If position charactor using effected three weapon, return True.
        """
        charactor = match.player_tables[position.player_idx].charactors[
            position.charactor_idx]
        return charactor.weapon_type in [
            WeaponType.SWORD, WeaponType.CLAYMORE, WeaponType.POLEARM]

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        If weapon type not right, do not enhance.
        """
        if not self.charactor_is_using_right_weapon(match, value.position):
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode)

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When source weapon type is sword, claymore or polearm, and talent
        activated, +1 normal attack DMG.
        """
        if not self.talent_activated:
            # talent not activated, do nothing
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not corresponding charactor, do nothing
            return value
        if not self.charactor_is_using_right_weapon(match, value.position):
            # not right weapon, do nothing
            return value
        # add damage
        assert mode == 'REAL'
        value.damage += 1
        return value


class IceLotus_3_3(DefendTeamStatus):
    name: Literal['Ice Lotus'] = 'Ice Lotus'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1


class FortunePreservingTalisman_4_0(UsageTeamStatus):
    name: Literal[
        'Fortune-Preserving Talisman'] = 'Fortune-Preserving Talisman'
    version: Literal['4.0'] = '4.0'
    usage: int = 3
    max_usage: int = 3
    newly_created: bool = True
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def renew(self, new_status: 'FortunePreservingTalisman_4_0') -> None:
        """
        Reset newly created
        """
        super().renew(new_status)
        self.newly_created = new_status.newly_created

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        if self.newly_created:
            # newly created, mark as false and no effect
            self.newly_created = False
            return []
        if event.action.position.player_idx != self.position.player_idx:
            # not our player skill made damage, do nothing
            return []
        assert event.action.position.area == ObjectPositionType.SKILL
        charactor = match.player_tables[self.position.player_idx].charactors[
            event.action.position.charactor_idx]
        if charactor.damage_taken <= 0:
            # no damage, do nothing
            return []
        # heal charactor
        self.usage -= 1
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        )]


class CatClawShield_3_3(ShieldTeamStatus):
    name: Literal['Cat-Claw Shield'] = 'Cat-Claw Shield'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1


class FlowingCicinShield_3_7(ShieldTeamStatus):
    name: Literal['Flowing Cicin Shield'] = 'Flowing Cicin Shield'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1


register_class(
    Icicle_3_3 | IcyQuill_3_7 | ChonghuasFrostField_3_3 | IceLotus_3_3 
    | FortunePreservingTalisman_4_0 | CatClawShield_3_3 
    | FlowingCicinShield_3_7
)
