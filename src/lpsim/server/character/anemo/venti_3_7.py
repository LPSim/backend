from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import SwirlChangeSummonBase

from ...event import RoundEndEventArguments

from ...action import (
    Actions,
    ChangeObjectUsageAction,
    MakeDamageAction,
    SwitchCharacterAction,
)
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
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


class Stormeye_3_7(SwirlChangeSummonBase):
    name: Literal["Stormeye"] = "Stormeye"
    version: Literal["3.7"] = "3.7"
    usage: int = 2
    max_usage: int = 2
    damage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction | SwitchCharacterAction]:
        """
        Need to change enemy active
        """
        ret: List[
            MakeDamageAction | ChangeObjectUsageAction | SwitchCharacterAction
        ] = []
        ret += super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[self.position.player_idx].active_character_idx
        target_characters = match.player_tables[1 - self.position.player_idx].characters
        target_idx = our_active
        if target_characters[target_idx].is_defeated:
            # need to choose another character
            for idx, character in enumerate(target_characters):
                if not character.is_defeated:
                    target_idx = idx
                    break
            else:
                raise AssertionError("No character alive")
        if (
            target_idx
            != match.player_tables[1 - self.position.player_idx].active_character_idx
        ):
            ret.append(
                SwitchCharacterAction(
                    player_idx=1 - self.position.player_idx,
                    character_idx=target_idx,
                )
            )
        return ret


# Skills


class SkywardSonnet(ElementalSkillBase):
    name: Literal["Skyward Sonnet"] = "Skyward Sonnet"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        assert character.name == "Venti"
        talent_activated = False
        if self.is_talent_equipped(match):
            talent_activated = True
        return super().get_actions(match) + [
            self.create_team_status("Stormzone", {"talent_activated": talent_activated})
        ]


class WindsGrandOde(ElementalBurstBase):
    name: Literal["Wind's Grand Ode"] = "Wind's Grand Ode"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        # create summon first, so it can change element immediately.
        return super().get_actions(match) + [self.create_summon("Stormeye")]


# Talents


class EmbraceOfWinds_3_7(SkillTalent):
    name: Literal["Embrace of Winds"]
    version: Literal["3.7"] = "3.7"
    character_name: Literal["Venti"] = "Venti"
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)
    skill: Literal["Skyward Sonnet"] = "Skyward Sonnet"


# character base


class Venti_3_7(CharacterBase):
    name: Literal["Venti"]
    version: Literal["3.7"] = "3.7"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | SkywardSonnet | WindsGrandOde] = []
    faction: List[FactionType] = [FactionType.MONDSTADT]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Divine Marksmanship",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SkywardSonnet(),
            WindsGrandOde(),
        ]


register_class(Venti_3_7 | EmbraceOfWinds_3_7 | Stormeye_3_7)
