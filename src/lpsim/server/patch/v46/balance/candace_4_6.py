from typing import Literal
from lpsim.server.action import Actions, RemoveObjectAction, SkipPlayerActionAction
from lpsim.server.character.character_base import PhysicalNormalAttackBase
from lpsim.server.character.hydro.candace_3_8 import (
    Candace_3_8,
    HeronStrike,
    SacredRiteHeronsSanctum as SRHS_3_8,
    SacredRiteWagtailsTide,
)
from lpsim.server.event import UseSkillEventArguments
from lpsim.server.match import Match
from lpsim.server.status.character_status.base import (
    PrepareCharacterStatus,
    ShieldCharacterStatus,
)
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType, duplicate_desc


class HeronShield_4_6(PrepareCharacterStatus):
    name: Literal["Heron Shield"] = "Heron Shield"
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Candace"] = "Candace"
    skill_name: Literal["Heron Strike"] = "Heron Strike"

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Match
    ) -> list[RemoveObjectAction | SkipPlayerActionAction]:
        ret = super().event_handler_USE_SKILL(event, match)
        if len(ret) > 0:
            # about to remove, also remove shield if exist
            target = self.query_one(match, "self status name='Heron Shield Shield'")
            if target is not None:
                ret.append(RemoveObjectAction(object_position=target.position))
        return ret


class HeronShieldShield_4_6(ShieldCharacterStatus):
    name: Literal["Heron Shield Shield"] = "Heron Shield Shield"
    version: Literal["4.6"] = "4.6"
    usage: int = 2
    max_usage: int = 2


class SacredRiteHeronsSanctum(SRHS_3_8):
    version: Literal["4.6"] = "4.6"

    def get_actions(self, match: Match) -> list[Actions]:
        """
        create status
        """
        return super().get_actions(match) + [
            self.create_character_status("Heron Shield Shield"),
        ]


class Candace_4_6(Candace_3_8):
    version: Literal["4.6"] = "4.6"
    skills: list[
        PhysicalNormalAttackBase
        | SacredRiteHeronsSanctum
        | SacredRiteWagtailsTide
        | HeronStrike
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Gleaming Spear - Guardian Stance",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SacredRiteHeronsSanctum(),
            SacredRiteWagtailsTide(),
            HeronStrike(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER_STATUS/Heron Shield Shield": {
        "names": {
            "zh-CN": "圣仪·苍鹭庇卫护盾",
            "en-US": "Heron Shield Shield",
        },
        "descs": {
            "4.6": {
                "en-US": "Provide 2 Shield points to the character to which this card is attached.",  # noqa: E501
                "zh-CN": "为所附属角色提供2点护盾。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Heron Shield": {
        "descs": {
            "4.6": {
                "zh-CN": "本角色将在下次行动时，直接使用技能：苍鹭震击。",
                "en-US": "The next time this character acts, they will immediately use the Skill Heron Strike.",  # noqa: E501
            }
        }
    },
}


duplicate_desc("3.8", "4.6", r"CHARACTER/Candace|SKILL_Candace")
register_class(Candace_4_6 | HeronShield_4_6 | HeronShieldShield_4_6, desc)
