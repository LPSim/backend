from typing import Dict, Literal

from .....utils.class_registry import register_class

from .....utils.desc_registry import DescDictType
from ....character.pyro.fatui_pyro_agent_3_3 import FatuiPyroAgent_3_3


class FatuiPyroAgent_4_3(FatuiPyroAgent_3_3):
    name: Literal["Fatui Pyro Agent"]
    version: Literal["4.3"] = "4.3"
    max_hp: int = 9


desc: Dict[str, DescDictType] = {
    "CHARACTER/Fatui Pyro Agent": {
        "descs": {"4.3": {"zh-CN": "", "en-US": ""}},
    },
    "SKILL_Fatui Pyro Agent_ELEMENTAL_BURST/Blade Ablaze": {
        "descs": {
            "4.3": {
                "zh-CN": "$SKILL_Fatui Pyro Agent_ELEMENTAL_BURST/Blade Ablaze|descs|3.3|zh-CN",  # noqa: E501
                "en-US": "$SKILL_Fatui Pyro Agent_ELEMENTAL_BURST/Blade Ablaze|descs|3.3|en-US",  # noqa: E501
            }
        }
    },
    "SKILL_Fatui Pyro Agent_ELEMENTAL_SKILL/Prowl": {
        "descs": {
            "4.3": {
                "zh-CN": "$SKILL_Fatui Pyro Agent_ELEMENTAL_SKILL/Prowl|descs|3.3|zh-CN",  # noqa: E501
                "en-US": "$SKILL_Fatui Pyro Agent_ELEMENTAL_SKILL/Prowl|descs|3.3|en-US",  # noqa: E501
            }
        }
    },
    "SKILL_Fatui Pyro Agent_NORMAL_ATTACK/Thrust": {
        "descs": {
            "4.3": {
                "zh-CN": "$SKILL_Fatui Pyro Agent_NORMAL_ATTACK/Thrust|descs|3.3|zh-CN",  # noqa: E501
                "en-US": "$SKILL_Fatui Pyro Agent_NORMAL_ATTACK/Thrust|descs|3.3|en-US",  # noqa: E501
            }
        }
    },
    "SKILL_Fatui Pyro Agent_PASSIVE/Stealth Master": {
        "descs": {
            "4.3": {
                "zh-CN": "$SKILL_Fatui Pyro Agent_PASSIVE/Stealth Master|descs|3.3|zh-CN",  # noqa: E501
                "en-US": "$SKILL_Fatui Pyro Agent_PASSIVE/Stealth Master|descs|3.3|en-US",  # noqa: E501
            }
        }
    },
}


register_class(FatuiPyroAgent_4_3, desc)
