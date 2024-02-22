from typing import Any, List, Literal

from ....utils.class_registry import register_class


from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import CharacterReviveEventArguments, SkillEndEventArguments

from ...action import Actions, CharacterReviveAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Summons


class HeraldOfFrost_4_0(AttackerSummonBase):
    name: Literal["Herald of Frost"] = "Herald of Frost"
    version: Literal["4.0"] = "4.0"
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        if event.action.position.player_idx != self.position.player_idx:
            # not our player skill made damage, do nothing
            return []
        assert event.action.position.area == ObjectPositionType.SKILL
        characters = match.player_tables[self.position.player_idx].characters
        character = characters[event.action.position.character_idx]
        if character.name != "Qiqi":
            # not Qiqi, do nothing
            return []
        if event.action.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack, do nothing
            return []
        # select character with most damage taken
        selected_character = character
        for c in characters:
            if c.is_alive and c.damage_taken > selected_character.damage_taken:
                selected_character = c
        # heal character
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=selected_character.position,
                        damage=-1,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=Cost(),
                    )
                ],
            )
        ]


# Skills


class AdeptusArtHeraldOfFrost(ElementalSkillBase):
    name: Literal["Adeptus Art: Herald of Frost"] = "Adeptus Art: Herald of Frost"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [
            self.charge_self(1),
            self.create_summon("Herald of Frost"),
        ]


class AdeptusArtPreserverOfFortune(ElementalBurstBase):
    name: Literal[
        "Adeptus Art: Preserver of Fortune"
    ] = "Adeptus Art: Preserver of Fortune"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=3, charge=3
    )

    revive_usage: int = 2

    def event_handler_CHARACTER_REVIVE(
        self, event: CharacterReviveEventArguments, match: Any
    ) -> List[Actions]:
        """
        When self is revived, reset revive usage
        """
        if (
            event.action.player_idx == self.position.player_idx
            and event.action.character_idx == self.position.character_idx
        ):
            self.revive_usage = 2
        return []

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Make damage and create status. Then if has talent and has revive usage,
        revive all defeated characters with 2 hp.
        """
        ret = super().get_actions(match) + [
            self.create_team_status("Fortune-Preserving Talisman")
        ]
        if not self.is_talent_equipped(match):
            # no talent
            return ret
        # has talent
        if self.revive_usage <= 0:
            # no revive usage
            return ret
        defeated_characters: List[CharacterBase] = []
        characters = match.player_tables[self.position.player_idx].characters
        for c in characters:
            if c.is_defeated:
                defeated_characters.append(c)
        if len(defeated_characters) == 0:
            # no defeated character
            return ret
        # has defeated character, revive them
        self.revive_usage -= 1
        for c in defeated_characters:
            ret.append(
                CharacterReviveAction(
                    player_idx=self.position.player_idx,
                    character_idx=c.position.character_idx,
                    revive_hp=2,
                )
            )
        return ret


# Talents


class RiteOfResurrection_4_0(SkillTalent):
    name: Literal["Rite of Resurrection"]
    version: Literal["4.0"] = "4.0"
    character_name: Literal["Qiqi"] = "Qiqi"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=5, charge=3
    )
    skill: Literal[
        "Adeptus Art: Preserver of Fortune"
    ] = "Adeptus Art: Preserver of Fortune"


# character base


class Qiqi_4_0(CharacterBase):
    name: Literal["Qiqi"]
    version: Literal["4.0"] = "4.0"
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase
        | AdeptusArtHeraldOfFrost
        | AdeptusArtPreserverOfFortune
    ] = []
    faction: List[FactionType] = [FactionType.LIYUE]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Ancient Sword Art",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            AdeptusArtHeraldOfFrost(),
            AdeptusArtPreserverOfFortune(),
        ]


register_class(Qiqi_4_0 | RiteOfResurrection_4_0 | HeraldOfFrost_4_0)
