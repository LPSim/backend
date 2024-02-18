from typing import Any, List, Literal

from ...event import CharacterReviveEventArguments

from ....utils.class_registry import register_class

from ...summon.base import AOESummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    WeaponType,
)
from ..character_base import (
    AOESkillBase,
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Summons


class SacredCryoPearl_3_3(AOESummonBase):
    name: Literal["Sacred Cryo Pearl"] = "Sacred Cryo Pearl"
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1
    back_damage: int = 1


# Skills


class TrailOftheQilin(ElementalSkillBase):
    name: Literal["Trail of the Qilin"] = "Trail of the Qilin"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status("Ice Lotus"),
        ]


class FrostflakeArrow(ElementalNormalAttackBase, AOESkillBase):
    name: Literal["Frostflake Arrow"] = "Frostflake Arrow"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    back_damage: int = 2
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=5)

    use_counter: int = 0

    def event_handler_CHARACTER_REVIVE(
        self, event: CharacterReviveEventArguments, match: Any
    ) -> List[Actions]:
        """
        When self is revived, clear counter
        """
        if (
            event.action.player_idx == self.position.player_idx
            and event.action.character_idx == self.position.character_idx
        ):
            self.use_counter = 0
        return []

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, if has talent, back damage increase
        """
        self.use_counter += 1
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.talent is not None:
            # if have talent, may increase damage
            if self.use_counter >= 2:
                # condition satisfied
                self.back_damage = 3
                if character.talent.version == "3.3":
                    # if is old talent
                    self.damage = 3
            else:
                self.back_damage = 2
                self.damage = 2
        return super().get_actions(match)


class CelestialShower(ElementalBurstBase, AOESkillBase):
    name: Literal["Celestial Shower"] = "Celestial Shower"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    back_damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=3, charge=3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [self.create_summon("Sacred Cryo Pearl")]


# Talents


class UndividedHeart_3_7(SkillTalent):
    name: Literal["Undivided Heart"]
    version: Literal["3.7"] = "3.7"
    character_name: Literal["Ganyu"] = "Ganyu"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO,
        elemental_dice_number=5,
    )
    skill: Literal["Frostflake Arrow"] = "Frostflake Arrow"


# character base


class Ganyu_3_7(CharacterBase):
    name: Literal["Ganyu"]
    version: Literal["3.7"] = "3.7"
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | TrailOftheQilin | FrostflakeArrow | CelestialShower
    ] = []
    faction: List[FactionType] = [FactionType.LIYUE]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Liutian Archery",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TrailOftheQilin(),
            FrostflakeArrow(),
            CelestialShower(),
        ]


register_class(Ganyu_3_7 | UndividedHeart_3_7 | SacredCryoPearl_3_3)
