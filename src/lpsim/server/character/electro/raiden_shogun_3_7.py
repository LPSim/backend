from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import DamageIncreaseValue

from ...summon.base import AttackerSummonBase

from ...action import Actions, ChargeAction
from ...struct import Cost

from ...consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    SkillType,
    WeaponType,
)
from ..character_base import (
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Summons


class EyeOfStormyJudgment_3_7(AttackerSummonBase):
    name: Literal["Eye of Stormy Judgment"] = "Eye of Stormy Judgment"
    version: Literal["3.7"] = "3.7"
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        assert mode == "REAL"
        if (
            not value.is_corresponding_character_use_damage_skill(
                self.position, match, SkillType.ELEMENTAL_BURST
            )
            or value.damage_elemental_type == DamageElementalType.PIERCING
            or value.damage_from_element_reaction
        ):
            # not corresponding character use elemental burst, or is piercing
            # damage, or damage is from element reaction
            return value
        # add damage
        value.damage += 1
        return value


# Skills


class TranscendenceBalefulOmen(ElementalSkillBase):
    name: Literal["Transcendence: Baleful Omen"] = "Transcendence: Baleful Omen"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [self.charge_self(1), self.create_summon("Eye of Stormy Judgment")]


class SecretArtMusouShinsetsu(ElementalBurstBase):
    name: Literal["Secret Art: Musou Shinsetsu"] = "Secret Art: Musou Shinsetsu"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=4, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        table = match.player_tables[self.position.player_idx]
        for cid, character in enumerate(table.characters):
            if character.is_alive and cid != self.position.character_idx:
                ret.append(
                    ChargeAction(
                        player_idx=self.position.player_idx,
                        character_idx=cid,
                        charge=2,
                    )
                )
        return ret


class ChakraDesiderata(CreateStatusPassiveSkill):
    name: Literal["Chakra Desiderata"] = "Chakra Desiderata"
    status_name: Literal["Chakra Desiderata"] = "Chakra Desiderata"


# Talents


class WishesUnnumbered_3_7(SkillTalent):
    name: Literal["Wishes Unnumbered"]
    version: Literal["3.7"] = "3.7"
    character_name: Literal["Raiden Shogun"] = "Raiden Shogun"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=4, charge=2
    )
    skill: Literal["Secret Art: Musou Shinsetsu"] = "Secret Art: Musou Shinsetsu"


# character base


class RaidenShogun_3_7(CharacterBase):
    name: Literal["Raiden Shogun"]
    version: Literal["3.7"] = "3.7"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | TranscendenceBalefulOmen
        | SecretArtMusouShinsetsu
        | ChakraDesiderata
    ] = []
    faction: List[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Origin",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TranscendenceBalefulOmen(),
            SecretArtMusouShinsetsu(),
            ChakraDesiderata(),
        ]


register_class(RaidenShogun_3_7 | WishesUnnumbered_3_7 | EyeOfStormyJudgment_3_7)
