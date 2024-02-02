from typing import Dict, Literal

from ....status.team_status.event_cards import (
    WindAndFreedom_4_1 as WindAndFreedomStatus_4_1,
)

from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType
from ....struct import Cost
from ....card.event.resonance import WindAndFreedom_4_1


class WindAndFreedomStatus_4_3(WindAndFreedomStatus_4_1):
    version: Literal["4.3"] = "4.3"


class WindAndFreedom_4_3(WindAndFreedom_4_1):
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Wind and Freedom": {
        "descs": {
            "4.3": {
                "zh-CN": "$TEAM_STATUS/Wind and Freedom|descs|4.1|zh-CN",
                "en-US": "$TEAM_STATUS/Wind and Freedom|descs|4.1|en-US",
            }
        },
    },
    "CARD/Wind and Freedom": {
        "descs": {
            "4.3": {
                "zh-CN": "$CARD/Wind and Freedom|descs|4.1|zh-CN",
                "en-US": "$CARD/Wind and Freedom|descs|4.1|en-US",
            }
        },
    },
}


register_class(WindAndFreedomStatus_4_3 | WindAndFreedom_4_3, desc)
