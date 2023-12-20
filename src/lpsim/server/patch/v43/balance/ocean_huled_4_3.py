
from typing import Dict, List, Literal
from pydantic import PrivateAttr

from .....utils.class_registry import register_class

from .....utils.desc_registry import DescDictType

from ....consts import DamageElementalType, DamageType

from ....modifiable_values import DamageValue

from ....action import Actions, MakeDamageAction

from ....struct import Cost

from ....card.equipment.artifact.ocean_hued import OceanHuedClam_4_2

from ....match import Match


class OceanHuedClam_4_3(OceanHuedClam_4_2):
    name: Literal['Ocean-Hued Clam']
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost(any_dice_number = 3)
    _heal: int = PrivateAttr(2)

    def equip(self, match: Match) -> List[Actions]:
        super().equip(match)
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        # heal self
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        target_position = charactor.position,
                        damage_type = DamageType.HEAL,
                        damage = -self._heal,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = Cost()
                    )
                ]
            )
        ]


desc: Dict[str, DescDictType] = {

    "ARTIFACT/Ocean-Hued Clam": {
        "descs": {
            "4.3": {
                "zh-CN": "入场时：治疗所附属角色2点。我方角色每受到3点治疗，此牌就累积1个「海染泡沫」。（最多累积2个）角色造成伤害时：消耗所有「海染泡沫」，每消耗1个都使造成的伤害+1。（角色最多装备1件「圣遗物」）",  # noqa: E501
                "en-US": "When played: Heal this charactor by 2 HP. For every 3 HP of healing your characters receive, this card accumulates 1 Sea-Dyed Foam (maximum of 2). When this character deals DMG: Consume all Sea-Dyed Foam. DMG is increased by 1 for each Sea-Dyed Foam consumed. (Characters can equip at most 1 Artifact)"  # noqa: E501
            }
        },
    },
}


register_class(OceanHuedClam_4_3, desc)
