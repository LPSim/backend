from typing import Dict, List, Literal

from ....charactor.charactor_base import SkillBase
from ....event import SkillEndEventArguments
from ....status.charactor_status.base import RoundCharactorStatus
from ....match import Match
from ....card.equipment.weapon.base import WeaponBase
from ....action import (
    CreateDiceAction, CreateObjectAction, RemoveObjectAction
)
from ....consts import (
    ELEMENT_TO_DIE_COLOR, IconType, ObjectPositionType, SkillType, WeaponType
)
from ....struct import Cost
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType


class SapwoodBladeStatus_4_4(RoundCharactorStatus):
    name: Literal['Sapwood Blade']
    version: Literal['4.4'] = '4.4'
    usage: int = 1
    max_usage: int = 1
    # TODO check icon
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        When self use normal attack, create 2 elemental dice.
        """
        position = event.action.position
        if not self.position.check_position_valid(
            position, match, player_idx_same = True,
            charactor_idx_same = True,
        ):
            # not self use skill
            return []
        skill: SkillBase = match.get_object(position)  # type: ignore
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not using normal attack
            return []
        charactor = match.player_tables[position.player_idx].charactors[
            position.charactor_idx]
        assert self.usage > 0
        self.usage -= 1
        return [CreateDiceAction(
            player_idx = position.player_idx,
            color = ELEMENT_TO_DIE_COLOR[charactor.element],
            number = 2,
        )] + self.check_should_remove()


class SapwoodBlade_4_4(WeaponBase):
    name: Literal['Sapwood Blade']
    version: Literal['4.4'] = '4.4'
    weapon_type: WeaponType = WeaponType.SWORD
    cost: Cost = Cost(any_dice_number = 3)

    def equip(self, match: Match) -> List[CreateObjectAction]:
        """
        attach status
        """
        return [CreateObjectAction(
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_name = self.name,
            object_arguments = {}
        )]


desc: Dict[str, DescDictType] = {
    "CHARACTOR_STATUS/Sapwood Blade": {
        "names": {
            "en-US": "Sapwood Blade",
            "zh-CN": "原木刀"
        },
        "descs": {
            "4.4": {
                "en-US": "When this character next uses a Normal Attack during this Round: Create 2 Elemental Dice of this character's Elemental Type.",  # noqa: E501
                "zh-CN": "本回合中，下次使用「普通攻击」后：生成2个此角色类型的元素骰。"  # noqa: E501
            }
        },
    },
    "WEAPON/Sapwood Blade": {
        "names": {
            "en-US": "Sapwood Blade",
            "zh-CN": "原木刀"
        },
        "descs": {
            "4.4": {
                "en-US": "The character deals +1 DMG.\nWhen entering play: When the character to which this is attached next uses a Normal Attack during this Round: Create 2 Elemental Dice of this character's Elemental Type.\n(Only Sword Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n入场时：所附属角色在本回合中，下次使用「普通攻击」后：生成2个此角色类型的元素骰。\n（「单手剑」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Weapon_Yuanmu.png",  # noqa: E501
        "id": 311507
    },
}


register_class(SapwoodBlade_4_4 | SapwoodBladeStatus_4_4, desc)
