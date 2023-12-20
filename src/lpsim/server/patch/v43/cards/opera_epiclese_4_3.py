from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....action import CreateDiceAction, RemoveObjectAction
from ....match import Match
from ....event import PlayerActionStartEventArguments
from ....consts import ELEMENT_TO_DIE_COLOR, IconType, ObjectPositionType
from ....struct import Cost
from ....card.support.base import UsageWithRoundRestrictionSupportBase
from ....card.support.locations import LocationBase
from .....utils.desc_registry import DescDictType


class OperaEpiclese_4_3(LocationBase, UsageWithRoundRestrictionSupportBase):
    name: Literal['Opera Epiclese']
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 3
    max_usage_one_round: int = 1
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        If self action start, and has usage, and no elemental dice, create
        one omni element.
        """
        if not (
            self.position.area == ObjectPositionType.SUPPORT
            and event.player_idx == self.position.player_idx
            and self.has_usage()
        ):
            # not equipped, or not self, or no usage
            return []
        equip_costs = [0] * len(match.player_tables)
        for player_idx, player_table in enumerate(match.player_tables):
            for charactor in player_table.charactors:
                equips = [
                    charactor.weapon, charactor.artifact, charactor.talent
                ]
                for equip in equips:
                    if equip is not None:
                        equip_costs[player_idx] += equip.cost.total_dice_cost
        if (
            equip_costs[self.position.player_idx] 
            < equip_costs[1 - self.position.player_idx]
        ):
            # not less than opponent, return
            return []
        # create one element die of active charactor
        self.use()
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 1,
            color = ELEMENT_TO_DIE_COLOR[active_charactor.element]
        )] + self.check_should_remove()


desc: Dict[str, DescDictType] = {
    "SUPPORT/Opera Epiclese": {
        "names": {
            "en-US": "Opera Epiclese",
            "zh-CN": "欧庇克莱歌剧院"
        },
        "descs": {
            "4.3": {
                "en-US": "Before you choose an action: If the original Elemental Dice cost of the cards equipped to your characters is not less than that of the opposing side, create 1 Elemental Die of your active character's element. (Once per Round)\nUsage(s): 3",  # noqa: E501
                "zh-CN": "我方选择行动前：如果我方角色所装备卡牌的原本元素骰费用总和不比对方更低，则生成1个出战角色类型的元素骰。（每回合1次）\n可用次数：3"  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Location_Gejuyuan.png",  # noqa: E501
        "id": 321017
    },
}


register_class(OperaEpiclese_4_3, desc)
