from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions, RemoveObjectAction
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    SkillTalent,
)


# Skills


class InfluxBlast(ElementalSkillBase):
    name: Literal["Influx Blast"] = "Influx Blast"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        First remove existing Refraction on opposite, then create new
        Refraction.
        """
        exist_status = self.query_one(
            match, "opponent character status name=Refraction"
        )
        ret: List[RemoveObjectAction] = []
        if exist_status is not None:
            ret.append(RemoveObjectAction(object_position=exist_status.position))
        args = {}
        if self.is_talent_equipped(match):
            args = {
                "usage": 3,
                "max_usage": 3,
                "is_talent_activated": True,
            }
        o_status = self.create_opposite_character_status(match, "Refraction", args)
        if len(ret) > 0 and o_status.object_position.check_position_valid(
            ret[0].object_position, match, player_idx_same=True, character_idx_same=True
        ):
            # attach to same character, do not remove
            ret = []
        return (
            ret
            + super().get_actions(match)
            + [self.create_opposite_character_status(match, "Refraction", args)]
        )


# Talents


class MirrorCage_3_3(SkillTalent):
    name: Literal["Mirror Cage"]
    version: Literal["3.3"]
    character_name: Literal["Mirror Maiden"] = "Mirror Maiden"
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=4)
    skill: Literal["Influx Blast"] = "Influx Blast"


class MirrorCage_4_2(MirrorCage_3_3):
    version: Literal["4.2"] = "4.2"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO,
        elemental_dice_number=3,
    )


# character base


class MirrorMaiden_3_7(CharacterBase):
    name: Literal["Mirror Maiden"]
    version: Literal["3.7"] = "3.7"
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[ElementalNormalAttackBase | InfluxBlast | ElementalBurstBase] = []
    faction: List[FactionType] = [FactionType.FATUI]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Water Ball",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            InfluxBlast(),
            ElementalBurstBase(
                name="Rippled Reflection",
                damage=5,
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalBurstBase.get_cost(self.element, 3, 2),
            ),
        ]


register_class(MirrorMaiden_3_7 | MirrorCage_4_2 | MirrorCage_3_3)
