from typing import Literal
from lpsim.server.action import CreateDiceAction
from lpsim.server.card.equipment.artifact.base import RoundEffectArtifactBase
from lpsim.server.consts import DamageElementalType, DamageType
from lpsim.server.event import ReceiveDamageEventArguments
from lpsim.server.match import Match
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class AmethystCrown_4_6(RoundEffectArtifactBase):
    name: Literal["Amethyst Crown"]
    version: Literal["4.6"] = "4.6"
    cost: Cost = Cost(same_dice_number=1)
    max_usage_per_round: int = 2
    counter: int = 0

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> list[CreateDiceAction]:
        damage = event.final_damage
        target = event.final_damage.target_position
        if self.position.not_satisfy(
            "source area=character active=true and both player=diff", target, match
        ):
            # self not active or damage ours
            return []
        if (
            damage.damage_elemental_type != DamageElementalType.DENDRO
            or damage.damage_type != DamageType.DAMAGE
        ):
            # not dendro damage
            return []
        self.counter += 1
        if self.counter < len(match.player_tables[self.position.player_idx].hands):
            # not enough
            return []
        if self.usage <= 0:
            return []
        self.usage -= 1
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=1,
                random=True,
            )
        ]


desc: dict[str, DescDictType] = {
    "ARTIFACT/Amethyst Crown": {
        "names": {"en-US": "Amethyst Crown", "zh-CN": "紫晶的花冠"},
        "descs": {
            "4.6": {
                "en-US": "After an opponent takes Dendro DMG when the character to which this is attached is the active character: Gain 1 Crowning Crystal. If your Crowning Crystal count is equal to or higher than the number of cards in your Hand, create 1 random basic Elemental Die.\n(Max 2 per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa
                "zh-CN": "所附属角色为出战角色，敌方受到草元素伤害后：累积1枚「花冠水晶」。如果「花冠水晶」大于等于我方手牌数，则生成1个随机基础元素骰。\n（每回合至多生成2个）\n（角色最多装备1件「圣遗物」）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Artifact_Zijinghuaguan.png",  # noqa
        "id": 312027,
    },
}


register_class(AmethystCrown_4_6, desc)
