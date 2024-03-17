from typing import Dict, Literal

from lpsim.server.card.support.locations import KnightsOfFavoniusLibrary_3_3
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class KnightsOfFavoniusLibrary_4_5(KnightsOfFavoniusLibrary_3_3):
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost()


desc: Dict[str, DescDictType] = {
    "SUPPORT/Knights of Favonius Library": {
        "descs": {
            "4.5": {
                "zh-CN": "$SUPPORT/Knights of Favonius Library|descs|3.3|zh-CN",
                "en-US": "$SUPPORT/Knights of Favonius Library|descs|3.3|en-US",
            }
        },
    },
}


register_class(KnightsOfFavoniusLibrary_4_5, desc)
