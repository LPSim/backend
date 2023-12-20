from typing import Dict, Literal

from .....utils.class_registry import register_class

from .....utils.desc_registry import DescDictType
from ....struct import Cost
from ....card.event.arcane_legend import JoyousCelebration_4_2


class JoyousCelebration_4_3(JoyousCelebration_4_2):
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost(arcane_legend = True)


desc: Dict[str, DescDictType] = {
    "ARCANE/Joyous Celebration": {
        "descs": {
            "4.3": {
                "zh-CN": "$ARCANE/Joyous Celebration|descs|4.2|zh-CN",
                "en-US": "$ARCANE/Joyous Celebration|descs|4.2|en-US"
            }
        },
    },
}


register_class(JoyousCelebration_4_3, desc)
