from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import AttackerSummonBase

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
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Summons


class ClusterbloomArrow_3_6(AttackerSummonBase):
    name: Literal["Clusterbloom Arrow"] = "Clusterbloom Arrow"
    version: Literal["3.6"] = "3.6"
    usage: int = 1
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 1
    renew_type: Literal["ADD"] = "ADD"


# Skills


class VijnanaPhalaMine(ElementalSkillBase):
    name: Literal["Vijnana-Phala Mine"] = "Vijnana-Phala Mine"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_character_status("Vijnana Suffusion"),
        ]


class FashionersTanglevineShaft(ElementalBurstBase, AOESkillBase):
    name: Literal["Fashioner's Tanglevine Shaft"] = "Fashioner's Tanglevine Shaft"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    back_damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3, charge=2
    )


# Talents


class KeenSight_3_6(SkillTalent):
    name: Literal["Keen Sight"]
    version: Literal["3.6"] = "3.6"
    character_name: Literal["Tighnari"] = "Tighnari"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.DENDRO,
        elemental_dice_number=4,
    )
    skill: Literal["Vijnana-Phala Mine"] = "Vijnana-Phala Mine"


# character base


class Tighnari_3_6(CharacterBase):
    name: Literal["Tighnari"]
    version: Literal["3.6"] = "3.6"
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | VijnanaPhalaMine | FashionersTanglevineShaft
    ] = []
    faction: List[FactionType] = [FactionType.SUMERU]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Khanda Barrier-Buster",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            VijnanaPhalaMine(),
            FashionersTanglevineShaft(),
        ]


register_class(Tighnari_3_6 | KeenSight_3_6 | ClusterbloomArrow_3_6)
