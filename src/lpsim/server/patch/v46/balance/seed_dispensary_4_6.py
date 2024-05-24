from typing import Dict, Literal

from pydantic import PrivateAttr

from lpsim.server.patch.v43.cards.seed_dispensary_4_3 import SeedDispensary_4_3
from lpsim.utils.class_registry import register_class
from lpsim.server.consts import CostLabels
from lpsim.utils.desc_registry import DescDictType


class SeedDispensary_4_6(SeedDispensary_4_3):
    version: Literal["4.6"] = "4.6"

    decrease_target: int = CostLabels.SUPPORTS.value
    _max_threshold: int = PrivateAttr(999)
    _min_threshold: int = PrivateAttr(2)


desc: Dict[str, DescDictType] = {
    "SUPPORT/Seed Dispensary": {
        "descs": {
            "4.6": {
                "en-US": "When you play a Support Card with an original cost of at least 2 Elemental Die: Spend 1 less Elemental Die. (Once per Round)\nUsage(s): 2",  # noqa: E501
                "zh-CN": "我方打出原本元素骰费用至少为2的支援牌时：少花费1个元素骰。（每回合1次）\n可用次数：2",  # noqa: E501
            }
        },
    },
}


register_class(SeedDispensary_4_6, desc)
