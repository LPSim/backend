from typing import Literal
from lpsim.server.action import Actions, RemoveObjectAction, SkipPlayerActionAction
from lpsim.server.character.character_base import PhysicalNormalAttackBase
from lpsim.server.character.electro.beidou_3_8 import (
    Beidou_3_8,
    Tidecaller as T_3_8,
    Stormbreaker,
    Wavestrider,
)
from lpsim.server.event import UseSkillEventArguments
from lpsim.server.match import Match
from lpsim.server.status.character_status.base import (
    PrepareCharacterStatus,
    ShieldCharacterStatus,
)
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType, duplicate_desc


class TidecallerSurfEmbrace_4_6(PrepareCharacterStatus):
    name: Literal["Tidecaller: Surf Embrace"] = "Tidecaller: Surf Embrace"
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Beidou"] = "Beidou"
    skill_name: Literal["Wavestrider"] = "Wavestrider"

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Match
    ) -> list[RemoveObjectAction | SkipPlayerActionAction]:
        ret = super().event_handler_USE_SKILL(event, match)
        if len(ret) > 0:
            # about to remove, also remove shield if exist
            target = self.query_one(
                match, "self status name='Tidecaller: Surf Embrace Shield'"
            )
            if target is not None:
                ret.append(RemoveObjectAction(object_position=target.position))
        return ret


class TidecallerSurfEmbraceShield_4_6(ShieldCharacterStatus):
    name: Literal["Tidecaller: Surf Embrace Shield"] = "Tidecaller: Surf Embrace Shield"
    version: Literal["4.6"] = "4.6"
    usage: int = 2
    max_usage: int = 2


class Tidecaller(T_3_8):
    version: Literal["4.6"] = "4.6"

    def get_actions(self, match: Match) -> list[Actions]:
        """
        create status
        """
        return super().get_actions(match) + [
            self.create_character_status("Tidecaller: Surf Embrace Shield"),
        ]


class Beidou_4_6(Beidou_3_8):
    version: Literal["4.6"] = "4.6"
    skills: list[
        PhysicalNormalAttackBase | Tidecaller | Wavestrider | Stormbreaker
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Oceanborne",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Tidecaller(),
            Wavestrider(),
            Stormbreaker(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER_STATUS/Tidecaller: Surf Embrace Shield": {
        "names": {
            "zh-CN": "捉浪护盾",
            "en-US": "Tidecaller: Surf Embrace",
        },
        "descs": {
            "4.6": {
                "en-US": "Provide 2 Shield points to the character to which this card is attached.",  # noqa: E501
                "zh-CN": "为所附属角色提供2点护盾。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Tidecaller: Surf Embrace": {
        "descs": {
            "4.6": {
                "zh-CN": "本角色将在下次行动时，直接使用技能：踏潮。",
                "en-US": "The next time this character acts, they will immediately use the Skill Wavestrider.",  # noqa: E501
            }
        }
    },
}


duplicate_desc("3.8", "4.6", r"CHARACTER/Beidou|SKILL_Beidou")
register_class(
    Beidou_4_6 | TidecallerSurfEmbrace_4_6 | TidecallerSurfEmbraceShield_4_6, desc
)
