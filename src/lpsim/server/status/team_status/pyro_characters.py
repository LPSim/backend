from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...struct import Cost

from ...modifiable_values import DamageDecreaseValue, DamageIncreaseValue, DamageValue

from ...consts import (
    DamageElementalType,
    DamageType,
    IconType,
    ObjectPositionType,
    SkillType,
)

from ...action import MakeDamageAction, RemoveObjectAction

from ...event import MakeDamageEventArguments, SkillEndEventArguments
from .base import (
    DefendTeamStatus,
    ExtraAttackTeamStatus,
    RoundTeamStatus,
    UsageTeamStatus,
)


class SparksNSplash_3_4(UsageTeamStatus):
    name: Literal["Sparks 'n' Splash"] = "Sparks 'n' Splash"
    version: Literal["3.4"] = "3.4"
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When attached character use skill, then damage itself.
        """
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not character use skill, not modify
            return []
        active_character = match.player_tables[
            self.position.player_idx
        ].get_active_character()
        if self.usage > 0:  # pragma: no branch
            self.usage -= 1
            return [
                MakeDamageAction(
                    damage_value_list=[
                        DamageValue(
                            position=self.position,
                            damage_type=DamageType.DAMAGE,
                            target_position=active_character.position,
                            damage=2,
                            damage_elemental_type=DamageElementalType.PYRO,
                            cost=Cost(),
                        )
                    ]
                )
            ]
        else:
            return []  # pragma: no cover


class InspirationField_3_3(RoundTeamStatus):
    name: Literal["Inspiration Field"] = "Inspiration Field"
    desc: Literal["", "talent"] = ""
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    talent_activated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = "talent"

    def renew(self, new_status: "InspirationField_3_3") -> None:
        super().renew(new_status)
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = "talent"

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        If character HP greater than 7, or talent activated, increase damage
        by 2
        """
        assert mode == "REAL"
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not our character use skill, do nothing
            return value
        character = match.player_tables[value.position.player_idx].characters[
            value.position.character_idx
        ]
        if not self.talent_activated and character.hp < 7:
            # no talent and hp less than 7, do nothing
            return value
        # increase damage by 2
        value.damage += 2
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If our character use skill and HP less than 7, heal 2 HP
        """
        if self.position.player_idx != event.action.position.player_idx:
            # not our character, do nothing
            return []
        character = match.player_tables[event.action.position.player_idx].characters[
            event.action.position.character_idx
        ]
        if character.hp > 6:
            # HP greater than 6, do nothing
            return []
        # heal this character by 2
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=character.position,
                        damage=-2,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=Cost(),
                    )
                ],
            )
        ]


class AurousBlaze_3_3(RoundTeamStatus, ExtraAttackTeamStatus):
    name: Literal["Aurous Blaze"] = "Aurous Blaze"
    version: Literal["3.3"] = "3.3"
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
        active character.
        """
        character = match.player_tables[self.position.player_idx].get_active_character()
        if character.name == "Yoimiya":
            # yoimiya use skill
            return []
        return super().event_handler_SKILL_END(event, match)


class Pyronado_3_3(UsageTeamStatus, ExtraAttackTeamStatus):
    name: Literal["Pyronado"] = "Pyronado"
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    trigger_skill_type: SkillType | None = None
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    decrease_usage: bool = True

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        skill = match.get_object(event.action.position)
        if skill.name == "Pyronado":
            # Xiangling use burst Pyronado
            return []
        return super().event_handler_SKILL_END(event, match)


class FierySanctumField_4_1(DefendTeamStatus):
    name: Literal["Fiery Sanctum Field"] = "Fiery Sanctum Field"
    version: Literal["4.1"] = "4.1"
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    decrease_usage_by_damage: bool = False

    def _find_dehya(self, match: Any) -> int:
        """
        Find first alive and standby dehya. If not found, return -1.
        """
        characters = match.player_tables[self.position.player_idx].characters
        active_idx = match.player_tables[self.position.player_idx].active_character_idx
        for cidx, character in enumerate(characters):
            if character.name == "Dehya" and character.is_alive and cidx != active_idx:
                return cidx
        return -1

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, mode: Literal["TEST", "REAL"]
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
            # check if should attack dehya
            dehya_idx = self._find_dehya(match)
            assert dehya_idx != -1
            dehya = match.player_tables[self.position.player_idx].characters[dehya_idx]
            if dehya.hp >= 7 and dehya.is_alive:
                # after shield triggered, dehya has at least 7 hp and alive,
                # make 1 piercing damage to dehya
                ret.append(
                    MakeDamageAction(
                        damage_value_list=[
                            DamageValue(
                                position=self.position,
                                target_position=dehya.position,
                                damage=1,
                                damage_type=DamageType.DAMAGE,
                                damage_elemental_type=DamageElementalType.PIERCING,
                                cost=Cost(),
                            )
                        ]
                    )
                )
        return ret + super().event_handler_MAKE_DAMAGE(event, match)


register_class(
    SparksNSplash_3_4
    | InspirationField_3_3
    | AurousBlaze_3_3
    | Pyronado_3_3
    | FierySanctumField_4_1
)
