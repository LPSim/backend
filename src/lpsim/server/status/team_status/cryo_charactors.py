from typing import Any, List, Literal

from ...event import (
    ChooseCharactorEventArguments, RoundPrepareEventArguments, 
    SkillEndEventArguments, SwitchCharactorEventArguments
)

from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, ObjectPositionType, SkillType, WeaponType
)

from ...modifiable_values import (
    DamageElementEnhanceValue, DamageIncreaseValue, DamageValue
)

from ...action import MakeDamageAction
from .base import (
    DefendTeamStatus, RoundTeamStatus, UsageTeamStatus, 
    ElementalInfusionTeamStatus
)


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


class ChonghuasFrostField(ElementalInfusionTeamStatus, RoundTeamStatus):
    name: Literal["Chonghua's Frost Field"] = "Chonghua's Frost Field"
    desc: str = (
        "Your Sword, Claymore, and Polearm-wielding characters' Physical DMG "
        "is converted to Cryo DMG."
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    talent_activated: bool = False

    infused_elemental_type: DamageElementalType = DamageElementalType.CRYO

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.talent_activated:
            self.desc += (
                " And your Sword, Claymore, and Polearm-wielding character's "
                "Normal Attacks +1 DMG."
            )
            self.max_usage = 3
            self.usage = 3

    def renew(self, object: 'ChonghuasFrostField'):
        super().renew(object)
        self.talent_activated = object.talent_activated

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


class IceLotus(DefendTeamStatus):
    name: Literal['Ice Lotus'] = 'Ice Lotus'
    desc: str = (
        'When your active character receives DMG: Decreases DMG taken by 1.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1


class FortunePreservingTalisman(UsageTeamStatus):
    name: Literal[
        'Fortune-Preserving Talisman'] = 'Fortune-Preserving Talisman'
    desc: str = (
        'After your character uses a Skill: If that character does not have '
        'full HP, heal that character for 2 HP.'
    )
    version: Literal['4.0'] = '4.0'
    usage: int = 3
    max_usage: int = 3
    newly_created: bool = True

    def renew(self, new_status: 'FortunePreservingTalisman') -> None:
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
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
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


CryoTeamStatus = (
    Icicle | IcyQuill | ChonghuasFrostField | IceLotus 
    | FortunePreservingTalisman
)
