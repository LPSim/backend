from typing import Any, List, Literal

from ....utils.class_registry import register_class


from ...modifiable_values import DamageValue
from ...event import (
    CharacterReviveEventArguments,
    CreateObjectEventArguments,
    GameStartEventArguments,
    RoundEndEventArguments,
    SkillEndEventArguments,
)
from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PassiveSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillBase,
    SkillTalent,
)


# Skills


class AttachRiptideWhenSkillEnd(SkillBase):
    version: str

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When skill end, if is this skill, and target
        is alive, attach riptide to target.
        """
        if event.action.position.id != self.id:
            # not self skill
            return []
        target = match.player_tables[1 - self.position.player_idx].characters[
            event.action.target_position.character_idx
        ]
        if target.is_defeated:
            # target is defeated
            return []
        # attach riptide to target
        return [
            CreateObjectAction(
                object_name="Riptide",
                object_position=event.action.target_position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={"version": self.version},
            )
        ]


class FoulLegacyRagingTide(ElementalSkillBase, AttachRiptideWhenSkillEnd):
    name: Literal["Foul Legacy: Raging Tide"] = "Foul Legacy: Raging Tide"
    version: Literal["4.1"] = "4.1"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object then attack
        """
        return [
            # Tartaglia need to create the status first, otherwise cannot
            # receive the damage increase
            self.create_character_status("Melee Stance", {"version": self.version}),
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.charge_self(1),
        ]


class HavocObliteration(ElementalBurstBase, AttachRiptideWhenSkillEnd):
    name: Literal["Havoc: Obliteration"] = "Havoc: Obliteration"
    version: Literal["4.1"] = "4.1"
    damage: int = 7
    ranged_damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO,
        elemental_dice_number=3,
        charge=3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        ranged_found: bool = False
        melee_found: bool = False
        for status in character.status:
            if status.name == "Ranged Stance":
                ranged_found = True
            elif status.name == "Melee Stance":  # pragma: no branch
                melee_found = True
        if ranged_found and melee_found:
            raise AssertionError("Cannot be both ranged and melee stance")
        if not (ranged_found or melee_found):
            raise AssertionError("Must be ranged or melee stance")
        if ranged_found:
            # ranged damage, and reclaim 2 energy. riptide will attach in
            # skill end.
            return [
                self.charge_self(-3),
                self.attack_opposite_active(
                    match, self.ranged_damage, DamageElementalType.HYDRO
                ),
                self.charge_self(2),
            ]
        else:
            # 7 damage
            return super().get_actions(match)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If ranged stance, call super() to attach riptide.
        """
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        ranged_found: bool = False
        for status in character.status:
            if status.name == "Ranged Stance":
                ranged_found = True
                break
        if not ranged_found:
            # not ranged stance
            return []
        return super().event_handler_SKILL_END(event, match)


class TideWithholder(PassiveSkillBase):
    """
    Only generate Ranged Stance at game start, and generate riptide event
    handler for system. status switch will be controlled by two status
    themself.
    """

    name: Literal["Tide Withholder"] = "Tide Withholder"
    status_name: Literal["Ranged Stance"] = "Ranged Stance"
    version: Literal["4.1"] = "4.1"

    def event_handler_CHARACTER_REVIVE(
        self, event: CharacterReviveEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When character revive, gain status
        """
        if (
            event.action.player_idx != self.position.player_idx
            or event.action.character_idx != self.position.character_idx
        ):
            # not this character, do nothing
            return []
        return [
            self.create_character_status("Ranged Stance", {"version": self.version}),
        ]

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain ranged stance and system handler
        """
        return [
            self.create_character_status("Ranged Stance", {"version": self.version}),
        ]


# Talents


class AbyssalMayhemHydrospout_4_1(SkillTalent):
    name: Literal["Abyssal Mayhem: Hydrospout"]
    version: Literal["4.1"] = "4.1"
    character_name: Literal["Tartaglia"] = "Tartaglia"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO,
        elemental_dice_number=3,
    )
    skill: Literal["Foul Legacy: Raging Tide"] = "Foul Legacy: Raging Tide"
    only_active_character: bool = True

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Make 1 damage to character if affected by Riptide. When only active
        character (after 4.1), only check active character. Otherwise,
        check all characters.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return []
        ret: List[MakeDamageAction] = []
        active_idx = match.player_tables[
            1 - self.position.player_idx
        ].active_character_idx
        for cidx, character in enumerate(
            match.player_tables[1 - self.position.player_idx].characters
        ):
            if self.only_active_character and cidx != active_idx:
                continue
            for status in character.status:
                if status.name == "Riptide":
                    ret.append(
                        MakeDamageAction(
                            damage_value_list=[
                                DamageValue(
                                    position=self.position,
                                    damage_type=DamageType.DAMAGE,
                                    target_position=character.position,
                                    damage=1,
                                    damage_elemental_type=DamageElementalType.PIERCING,
                                    cost=Cost(),
                                )
                            ]
                        )
                    )
                    break
        return ret


# character base


class Tartaglia_4_1(CharacterBase):
    name: Literal["Tartaglia"]
    desc: Literal["", "transform"] = ""
    version: Literal["4.1"] = "4.1"
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase
        | FoulLegacyRagingTide
        | HavocObliteration
        | TideWithholder
    ] = []
    faction: List[FactionType] = [FactionType.FATUI]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Cutting Torrent",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            FoulLegacyRagingTide(),
            HavocObliteration(),
            TideWithholder(),
        ]

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[Actions]:
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if s.name == "Melee Stance":
                self.desc = "transform"
                return []
        self.desc = ""
        return []


register_class(Tartaglia_4_1 | AbyssalMayhemHydrospout_4_1)
