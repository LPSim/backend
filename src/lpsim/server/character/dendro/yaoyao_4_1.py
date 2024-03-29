from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import RoundEndEventArguments

from ...action import ActionTypes, Actions, ChangeObjectUsageAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DamageType,
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


class YueguiThrowingMode_4_1(AttackerSummonBase):
    name: Literal["Yuegui: Throwing Mode"] = "Yuegui: Throwing Mode"
    version: Literal["4.1"] = "4.1"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 1
    is_talent_activated: bool = False

    def renew(self, obj: "YueguiThrowingMode_4_1") -> None:
        self.is_talent_activated = obj.is_talent_activated
        super().renew(obj)

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        When in round end, attack enemy active character and heal our
        character. When talent activated, and usage is 1, damage is increased
        to 2.
        """
        if self.usage == 1 and self.is_talent_activated:
            self.damage = 2
        ret = super().event_handler_ROUND_END(event, match)
        table = match.player_tables[self.position.player_idx]
        characters = table.characters
        # select character with most damage taken
        selected_character = characters[table.active_character_idx]
        for c in characters:
            if c.is_alive and c.damage_taken > selected_character.damage_taken:
                selected_character = c
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        damage_action.damage_value_list.append(
            DamageValue(
                position=self.position,
                damage_type=DamageType.HEAL,
                target_position=selected_character.position,
                damage=-self.damage,
                damage_elemental_type=DamageElementalType.HEAL,
                cost=Cost(),
            )
        )
        return ret


# Skills


class RaphanusSkyCluster(ElementalSkillBase):
    name: Literal["Raphanus Sky Cluster"] = "Raphanus Sky Cluster"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        args = {}
        if self.is_talent_equipped(match):
            args["is_talent_activated"] = True
        return [self.create_summon("Yuegui: Throwing Mode", args), self.charge_self(1)]


class MoonjadeDescent(ElementalBurstBase):
    name: Literal["Moonjade Descent"] = "Moonjade Descent"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.DENDRO, elemental_dice_number=4, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [self.create_team_status("Adeptal Legacy")]


# Talents


class Beneficent_4_1(SkillTalent):
    name: Literal["Beneficent"]
    version: Literal["4.1"] = "4.1"
    character_name: Literal["Yaoyao"] = "Yaoyao"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.DENDRO,
        elemental_dice_number=3,
    )
    skill: Literal["Raphanus Sky Cluster"] = "Raphanus Sky Cluster"


# character base


class Yaoyao_4_1(CharacterBase):
    name: Literal["Yaoyao"]
    version: Literal["4.1"] = "4.1"
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | RaphanusSkyCluster | MoonjadeDescent] = []
    faction: List[FactionType] = [FactionType.LIYUE]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Toss 'N' Turn Spear",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            RaphanusSkyCluster(),
            MoonjadeDescent(),
        ]


register_class(Yaoyao_4_1 | Beneficent_4_1 | YueguiThrowingMode_4_1)
