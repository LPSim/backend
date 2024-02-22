from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageIncreaseValue, DamageValue

from ...action import (
    Actions,
    ChangeObjectUsageAction,
    MakeDamageAction,
    SwitchCharacterAction,
)
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


class DandelionField_3_3(AttackerSummonBase):
    name: Literal["Dandelion Field"] = "Dandelion Field"
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    damage: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self,
        value: DamageIncreaseValue,
        match: Any,
        mode: Literal["TEST", "REAL"],
    ) -> DamageIncreaseValue:
        """
        If found Jean with talent, increase anemo damage by 1
        """
        if (
            value.damage_type != DamageType.DAMAGE
            or value.damage_elemental_type != DamageElementalType.ANEMO
            or value.position.player_idx != self.position.player_idx
            or value.target_position.player_idx == self.position.player_idx
        ):
            # not anemo damage, or not from our side attack enemy
            return value
        # find jean with talent
        characters = match.player_tables[self.position.player_idx].characters
        for character in characters:
            if character.name == "Jean" and character.talent is not None:
                # found, increase damage
                assert mode == "REAL"
                value.damage += 1
                return value
        return value

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[
            self.position.player_idx
        ].get_active_character()
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=our_active.position,
                        damage=-1,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=Cost(),
                    )
                ],
            )
        )
        return ret


# Skills


class GaleBlade(ElementalSkillBase):
    name: Literal["Gale Blade"] = "Gale Blade"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        next_idx = match.player_tables[
            1 - self.position.player_idx
        ].next_character_idx()
        if next_idx is None:
            return super().get_actions(match)
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type),
            SwitchCharacterAction(
                player_idx=1 - self.position.player_idx, character_idx=next_idx
            ),
            self.charge_self(1),
        ]


class DandelionBreeze(ElementalBurstBase):
    name: Literal["Dandelion Breeze"] = "Dandelion Breeze"
    damage: int = -2
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=4, charge=3
    )
    version: Literal["3.3"] = "3.3"

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = [self.charge_self(-self.cost.charge)]
        characters = match.player_tables[self.position.player_idx].characters
        heal_action = MakeDamageAction(
            damage_value_list=[],
        )
        for character in characters:
            if character.is_alive:
                heal_action.damage_value_list.append(
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=character.position,
                        damage=self.damage,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=self.cost.copy(),
                    )
                )
        ret.append(heal_action)
        ret.append(self.create_summon("Dandelion Field", {"version": self.version}))
        return ret


# Talents


class LandsOfDandelion_3_3(SkillTalent):
    name: Literal["Lands of Dandelion"]
    version: Literal["3.3"] = "3.3"
    character_name: Literal["Jean"] = "Jean"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=4, charge=3
    )
    skill: Literal["Dandelion Breeze"] = "Dandelion Breeze"


# character base


class Jean_3_3(CharacterBase):
    name: Literal["Jean"]
    version: Literal["3.3"] = "3.3"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[PhysicalNormalAttackBase | GaleBlade | DandelionBreeze] = []
    faction: List[FactionType] = [FactionType.MONDSTADT]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Favonius Bladework",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GaleBlade(),
            DandelionBreeze(),
        ]


register_class(Jean_3_3 | DandelionField_3_3 | LandsOfDandelion_3_3)
