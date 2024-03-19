from typing import Dict, List, Literal

from lpsim.server.action import CreateObjectAction
from lpsim.server.card.equipment.weapon.base import RoundEffectWeaponBase
from lpsim.server.consts import DamageType, IconType, ObjectPositionType, WeaponType
from lpsim.server.event import ReceiveDamageEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageIncreaseValue
from lpsim.server.status.character_status.base import (
    RoundCharacterStatus,
    UsageCharacterStatus,
)
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class TomeOfTheEternalFlowStatus_4_5(UsageCharacterStatus, RoundCharacterStatus):
    name: Literal["Tome of the Eternal Flow"] = "Tome of the Eternal Flow"
    version: Literal["4.5"] = "4.5"
    icon_type: IconType = IconType.ATK_UP  # TODO
    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        assert mode == "REAL"
        if self.usage <= 0:  # pragma: no cover
            # no usage, not modify
            return value
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not this character use skill, not modify
            return value
        # modify
        value.damage += 2
        self.usage -= 1
        return value


class TomeOfTheEternalFlow_4_5(RoundEffectWeaponBase):
    name: Literal["Tome of the Eternal Flow"] = "Tome of the Eternal Flow"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(same_dice_number=3)
    weapon_type: WeaponType = WeaponType.CATALYST
    # we use round effect to reset. when usage to 2, then create a status.
    max_usage_per_round: int = 0

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        if self.position.not_satisfy(
            "both pidx=same cidx=same", event.final_damage.target_position
        ):
            return []
        if event.final_damage.damage_type == DamageType.ELEMENT_APPLICATION:
            return []
        self.usage += 1
        if self.usage == 2:
            return [
                CreateObjectAction(
                    object_name="Tome of the Eternal Flow",
                    object_position=self.position.set_area(
                        ObjectPositionType.CHARACTER_STATUS
                    ),
                    object_arguments={},
                )
            ]
        return []


desc: Dict[str, DescDictType] = {
    "CHARACTER_STATUS/Tome of the Eternal Flow": {
        "names": {"en-US": "Tome of the Eternal Flow", "zh-CN": "万世流涌大典"},
        "descs": {
            "4.5": {
                "en-US": "This character's next attack this Round deals +2 additional DMG.",  # noqa: E501
                "zh-CN": "角色本回合中下次造成的伤害+2。",
            }
        },
    },
    "WEAPON/Tome of the Eternal Flow": {
        "names": {"en-US": "Tome of the Eternal Flow", "zh-CN": "万世流涌大典"},
        "descs": {
            "4.5": {
                "en-US": "The character deals +1 DMG.\nAfter this character takes DMG or is healed: If this character has already been damaged or healed 2 times this Round, then this character's next attack this Round deals +2 additional DMG. (Once per Round)\n(Only Catalyst Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n角色受到伤害或治疗后：如果本回合已受到伤害或治疗累计2次，则角色本回合中下次造成的伤害+2。（每回合1次）\n（「法器」角色才能装备。角色最多装备1件「武器」）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Wanshiliuyongdadian.png",  # noqa: E501
        "id": 311108,
    },
}


register_class(TomeOfTheEternalFlow_4_5 | TomeOfTheEternalFlowStatus_4_5, desc)
