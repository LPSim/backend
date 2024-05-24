from typing import List, Literal

from lpsim.server.action import MakeDamageAction, RemoveObjectAction, CreateObjectAction
from lpsim.server.character.pyro.abyss_lector_fathomless_flames_3_7 import (
    EmbersRekindled_3_7 as ER_3_7,
    FieryRebirth as FR_3_7,
    AbyssLectorFathomlessFlames_3_7,
    OminousStar,
)
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageIncreaseValue, DamageValue
from lpsim.server.status.character_status.base import (
    CharacterStatusBase,
    ReviveCharacterStatus,
    ShieldCharacterStatus,
)
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.server.consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DamageType,
    IconType,
)
from lpsim.server.character.character_base import (
    ElementalNormalAttackBase,
    ElementalSkillBase,
)
from lpsim.utils.desc_registry import DescDictType, duplicate_desc


class AegisOfAbyssalFlame_4_6(ShieldCharacterStatus):
    # TODO: when removed because piercing damage, should we attack opposite?
    # currently not, need further check. related to v46 abyss_fire_talent.json
    name: Literal["Aegis of Abyssal Flame"] = "Aegis of Abyssal Flame"
    version: Literal["4.6"] = "4.6"
    usage: int = 2
    max_usage: int = 2

    def check_should_remove(
        self, match: Match
    ) -> List[RemoveObjectAction | MakeDamageAction]:
        ret: List[RemoveObjectAction | MakeDamageAction] = list(
            super().check_should_remove()
        )
        if len(ret) > 0:
            targets = self.query(match, "opponent character")
            assert len(targets) > 0
            damage_action = MakeDamageAction(damage_value_list=[])
            for target in targets:
                damage_action.damage_value_list.append(
                    DamageValue(
                        position=self.position,
                        target_position=target.position,
                        damage_type=DamageType.DAMAGE,
                        damage_elemental_type=DamageElementalType.PIERCING,
                        damage=1,
                        cost=Cost(),
                    )
                )
            ret.append(damage_action)
        return ret


class FieryRebirthHoned_4_6(CharacterStatusBase):
    name: Literal["Fiery Rebirth: Honed"] = "Fiery Rebirth: Honed"
    version: Literal["4.6"] = "4.6"
    usage: int = 0
    max_usage: int = 0
    icon_type: IconType = IconType.ATK_UP_FIRE

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        increase pyro damage dealt by this character by 1.
        """
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding character use skill, do nothing
            return value
        if value.damage_elemental_type != DamageElementalType.PYRO:  # pragma: no cover
            # not pyro damage, do nothing
            return value
        value.damage += 1
        return value


class FieryRebirth_4_6(ReviveCharacterStatus):
    name: Literal["Fiery Rebirth"] = "Fiery Rebirth"
    version: Literal["4.6"] = "4.6"
    heal: int = 4

    def check_should_remove(self) -> List[RemoveObjectAction | CreateObjectAction]:
        """
        when remove, also generate new status
        """
        ret: List[RemoveObjectAction | CreateObjectAction] = list(
            super().check_should_remove()
        )
        if len(ret) > 0:  # pragma: no branch
            ret.append(
                CreateObjectAction(
                    object_position=self.position,
                    object_name="Fiery Rebirth: Honed",
                    object_arguments={},
                )
            )
        return ret


class FieryRebirth(FR_3_7):
    version: Literal["4.6"] = "4.6"


class EmbersRekindled_4_6(ER_3_7):
    version: Literal["4.6"] = "4.6"


# character base


class AbyssLectorFathomlessFlames_4_6(AbyssLectorFathomlessFlames_3_7):
    version: Literal["4.6"] = "4.6"
    skills: List[
        ElementalNormalAttackBase | ElementalSkillBase | OminousStar | FieryRebirth
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Flame of Salvation",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name="Searing Precept",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalSkillBase.get_cost(self.element),
            ),
            OminousStar(),
            FieryRebirth(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER_STATUS/Aegis of Abyssal Flame": {
        "descs": {
            "4.6": {
                "en-US": "Provide 2 Shield points to the character to which this card is attached.\nAfter said Shield points are depleted: Deal 1 Piercing DMG to all opposing characters.",  # noqa: E501
                "zh-CN": "为所附属角色提供2点护盾。\n此护盾耗尽后：对所有敌方角色造成1点穿透伤害。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Fiery Rebirth: Honed": {
        "names": {
            "en-US": "Fiery Rebirth: Honed",
            "zh-CN": "火之新生·锐势",
        },
        "descs": {
            "4.6": {
                "en-US": "Increase the Pyro DMG dealt by this character by 1.",  # noqa: E501
                "zh-CN": "此角色造成的火元素伤害+1",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Fiery Rebirth": {
        "descs": {
            "4.6": {
                "en-US": "When the character to which this is attached would be defeated: Remove this effect, ensure the character will not be defeated, and heal them to 4 HP. After this effect is triggered, this character deals +1 Pyro DMG.",  # noqa: E501
                "zh-CN": "所附属角色被击倒时：移除此效果，使角色免于被击倒，并治疗该角色到4点生命值。此效果触发后，角色造成的火元素伤害+1。",  # noqa: E501
            }
        },
    },
}


duplicate_desc("3.7", "4.6", r"CHARACTER/Abyss Lector: Fathomless Flames", r"")
duplicate_desc("3.7", "4.6", r"SKILL_Abyss Lector: Fathomless Flames", r"")
duplicate_desc("3.7", "4.6", r"TALENT_Abyss Lector: Fathomless Flames", r"")
register_class(
    AbyssLectorFathomlessFlames_4_6
    | AegisOfAbyssalFlame_4_6
    | FieryRebirthHoned_4_6
    | FieryRebirth_4_6
    | EmbersRekindled_4_6,
    desc,
)
