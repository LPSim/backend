from typing import List, Literal
from lpsim.server.action import (
    ActionTypes,
    Actions,
    CreateObjectAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from lpsim.server.character.character_base import (
    CharacterBase,
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    TalentBase,
)
from lpsim.server.consts import (
    CostLabels,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    WeaponType,
)
from lpsim.server.event import RemoveObjectEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import CostValue, DamageIncreaseValue
from lpsim.server.status.character_status.base import (
    ElementalInfusionCharacterStatus,
    PrepareCharacterStatus,
    ReviveCharacterStatus,
)
from lpsim.server.status.team_status.base import UsageTeamStatus
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class CurseOfTheUndercurrent_4_6(UsageTeamStatus):
    name: Literal["Curse of the Undercurrent"] = "Curse of the Undercurrent"
    version: Literal["4.6"] = "4.6"
    usage: int = 2
    max_usage: int = 2
    icon_type: IconType = IconType.OTHERS

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        if self.position.not_satisfy(
            "both pidx=same and target area=skill",
            target=value.position,
        ):
            # not our use skill
            return value
        if (
            value.cost.label & CostLabels.ELEMENTAL_SKILL.value == 0
            and value.cost.label & CostLabels.ELEMENTAL_BURST.value == 0
        ):
            # not skill or burst
            return value
        # increase cost
        assert value.cost.elemental_dice_color is not None
        value.cost.elemental_dice_number += 1
        if mode == "REAL":
            self.usage -= 1
        return value


class RipplingBlades_4_6(PrepareCharacterStatus):
    name: Literal["Rippling Blades"] = "Rippling Blades"
    version: Literal["4.6"] = "4.6"
    character_name: Literal[
        "Abyss Herald: Wicked Torrents"
    ] = "Abyss Herald: Wicked Torrents"
    skill_name: Literal["Rippling Blades"] = "Rippling Blades"


class WateryRebirthHoned_4_6(ElementalInfusionCharacterStatus):
    name: Literal["Watery Rebirth: Honed"] = "Watery Rebirth: Honed"
    version: Literal["4.6"] = "4.6"
    infused_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    usage: int = 1  # 1 usage to allow elemental infusion
    max_usage: int = 1
    icon_type: IconType = IconType.ATK_UP_WATER

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        increase hydro damage dealt by this character by 1.
        """
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding character use skill, do nothing
            return value
        if (
            value.damage_elemental_type != self.infused_elemental_type
        ):  # pragma: no cover  # noqa
            # not pyro damage, do nothing
            return value
        value.damage += 1
        return value


class WateryRebirth_4_6(ReviveCharacterStatus):
    name: Literal["Watery Rebirth"] = "Watery Rebirth"
    version: Literal["4.6"] = "4.6"
    heal: int = 4

    def check_should_remove(self) -> List[RemoveObjectAction | CreateObjectAction]:
        """
        when remove, also generate new status
        """
        ret: List[RemoveObjectAction | CreateObjectAction] = list(
            super().check_should_remove()
        )
        if len(ret) > 0:  # pragma: no branch
            ret.append(
                CreateObjectAction(
                    object_position=self.position,
                    object_name="Watery Rebirth: Honed",
                    object_arguments={},
                )
            )
        return ret


class VortexEdge(ElementalSkillBase):
    name: Literal["Vortex Edge"] = "Vortex Edge"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> list[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_character_status("Rippling Blades"),
        ]


class RipplingBlades(ElementalSkillBase):
    name: Literal["Rippling Blades"] = "Rippling Blades"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost()

    def is_valid(self, match: Match):
        return False

    def get_actions(self, match: Match) -> List[MakeDamageAction]:
        return [self.attack_opposite_active(match, self.damage, self.damage_type)]


class TorrentialShock(ElementalBurstBase):
    name: Literal["Torrential Shock"] = "Torrential Shock"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> list[Actions]:
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name="Curse of the Undercurrent",
                object_position=ObjectPosition(
                    player_idx=1 - self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        ]


class WateryRebirth(CreateStatusPassiveSkill):
    name: Literal["Watery Rebirth"] = "Watery Rebirth"
    status_name: Literal["Watery Rebirth"] = "Watery Rebirth"
    version: Literal["4.6"] = "4.6"
    regenerate_when_revive: bool = False


# Talents


class SurgingUndercurrent_4_6(TalentBase):
    name: Literal["Surging Undercurrent"]
    version: Literal["4.6"] = "4.6"
    character_name: Literal[
        "Abyss Herald: Wicked Torrents"
    ] = "Abyss Herald: Wicked Torrents"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO,
        elemental_dice_number=1,
    )

    available_handler_in_trashbin: list[ActionTypes] = [ActionTypes.REMOVE_OBJECT]

    def is_valid(self, match: Match) -> bool:
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError("Talent is not in hand")
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Match) -> list[ObjectPosition]:
        assert self.position.area != ObjectPositionType.CHARACTER
        ret: list[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].characters:
            if c.name == self.character_name and c.is_alive:
                ret.append(c.position)
        return ret

    def _create_curse(self) -> CreateObjectAction:
        return CreateObjectAction(
            object_name="Curse of the Undercurrent",
            object_position=ObjectPosition(
                player_idx=1 - self.position.player_idx,
                area=ObjectPositionType.TEAM_STATUS,
                id=0,
            ),
            object_arguments={},
        )

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> list[Actions]:
        # when self watery rebirth is removed, create curse
        print("XXX", self.position, event.action.object_position, event.object_name)
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return []
        if self.position.satisfy(
            "both pidx=same cidx=same and target area=CHARACTER_STATUS",
            target=event.action.object_position,
        ):
            if event.object_name == "Watery Rebirth":
                return [self._create_curse()]
        # when self is removed because of defeated, create curse
        character: CharacterBase = self.query_one(match, "self")  # type: ignore
        if character.is_alive:
            return []
        return [self._create_curse()]

    def get_actions(self, target: ObjectPosition | None, match: Match) -> List[Actions]:
        ret = super().get_actions(target, match)
        # if create target do not have watery rebirth, create curse
        assert target is not None
        tobj = match.get_object(target)
        assert tobj is not None
        watery_rebirth = tobj.query_one(match, 'self status name="Watery Rebirth"')
        if watery_rebirth is None:
            # not find, create curse
            ret.append(self._create_curse())
        return ret


# character base


# character class name should contain its version.
class AbyssHeraldWickedTorrents_4_6(CharacterBase):
    name: Literal["Abyss Herald: Wicked Torrents"]
    version: Literal["4.6"] = "4.6"
    element: ElementType = ElementType.HYDRO
    max_hp: int = 6
    max_charge: int = 2
    skills: list[
        PhysicalNormalAttackBase
        | VortexEdge
        | RipplingBlades
        | TorrentialShock
        | WateryRebirth
    ] = []
    faction: list[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Rippling Slash",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            VortexEdge(),
            RipplingBlades(),
            TorrentialShock(),
            WateryRebirth(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER/Abyss Herald: Wicked Torrents": {
        "names": {"en-US": "Abyss Herald: Wicked Torrents", "zh-CN": "深渊使徒·激流"},
        "descs": {"4.6": {"en-US": "", "zh-CN": ""}},
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Char_Monster_InvokerHeraldWater.png",  # noqa
        "id": 2203,
    },
    "SKILL_Abyss Herald: Wicked Torrents_NORMAL_ATTACK/Rippling Slash": {
        "names": {"en-US": "Rippling Slash", "zh-CN": "波刃锋斩"},
        "descs": {
            "4.6": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Abyss Herald: Wicked Torrents_ELEMENTAL_SKILL/Vortex Edge": {
        "names": {"en-US": "Vortex Edge", "zh-CN": "洄涡锋刃"},
        "descs": {
            "4.6": {
                "en-US": 'Deals 2 Hydro DMG, then performs "Prepare Skill|s1:prepares" for Rippling Blades.',  # noqa
                "zh-CN": "造成2点水元素伤害，然后准备技能：涟锋旋刃。",
            }
        },
    },
    "CHARACTER_STATUS/Rippling Blades": {
        "names": {"en-US": "Rippling Blades", "zh-CN": "涟锋旋刃"},
        "descs": {
            "4.6": {"en-US": "Deals 1 Hydro DMG.", "zh-CN": "造成1点水元素伤害。"}
        },
    },
    "SKILL_Abyss Herald: Wicked Torrents_ELEMENTAL_BURST/Torrential Shock": {
        "names": {"en-US": "Torrential Shock", "zh-CN": "激流强震"},
        "descs": {
            "4.6": {
                "en-US": "Deals 3 Hydro DMG. Creates 1 Curse of the Undercurrent on the opponent's side of the field.",  # noqa
                "zh-CN": "造成3点水元素伤害。在对方场上生成暗流的诅咒。",
            }
        },
    },
    "TEAM_STATUS/Curse of the Undercurrent": {
        "names": {"en-US": "Curse of the Undercurrent", "zh-CN": "暗流的诅咒"},
        "descs": {
            "4.6": {
                "en-US": "When character(s) on this side of the playing field use Elemental Skills or Elemental Bursts: They must spend 1 extra Elemental Die.\nUsage(s): 2",  # noqa
                "zh-CN": "所在阵营的角色使用元素战技或元素爆发时：需要多花费1个元素骰。\n可用次数：2",
            }
        },
    },
    "SKILL_Abyss Herald: Wicked Torrents_PASSIVE/Watery Rebirth": {
        "names": {"en-US": "Watery Rebirth", "zh-CN": "水之新生"},
        "descs": {
            "4.6": {
                "en-US": "(Passive) When the battle begins, this character gains Watery Rebirth.",  # noqa
                "zh-CN": "【被动】战斗开始时，初始附属水之新生。",
            }
        },
    },
    "CHARACTER_STATUS/Watery Rebirth: Honed": {
        "names": {"en-US": "Watery Rebirth: Honed", "zh-CN": "水之新生·锐势"},
        "descs": {
            "4.6": {
                "en-US": "Physical DMG this character deals is converted to Hydro DMG, and Hydro DMG +1.",  # noqa
                "zh-CN": "角色造成的物理伤害变为水元素伤害，且水元素伤害+1。",
            }
        },
    },
    "CHARACTER_STATUS/Watery Rebirth": {
        "names": {"en-US": "Watery Rebirth", "zh-CN": "水之新生"},
        "descs": {
            "4.6": {
                "en-US": "When the character to which this is attached would be defeated: Remove this effect, ensure the character not to be defeated, and heal them to 4 HP. After this effect is triggered, Physical DMG this character deals is converted to Hydro DMG, and Hydro DMG +1.",  # noqa
                "zh-CN": "所附属角色被击倒时：移除此效果，使角色免于被击倒，并治疗该角色到4点生命值。此效果触发后，角色造成的物理伤害变为水元素伤害，且水元素伤害+1。",  # noqa
            }
        },
    },
    "SKILL_Abyss Herald: Wicked Torrents_ELEMENTAL_SKILL/Rippling Blades": {
        "names": {"en-US": "Rippling Blades", "zh-CN": "涟锋旋刃"},
        "descs": {
            "4.6": {"en-US": "Deals 1 Hydro DMG.", "zh-CN": "造成1点水元素伤害。"}
        },
    },
    "TALENT_Abyss Herald: Wicked Torrents/Surging Undercurrent": {
        "names": {"en-US": "Surging Undercurrent", "zh-CN": "暗流涌动"},
        "descs": {
            "4.6": {
                "en-US": "When played: If Abyss Herald: Wicked Torrents, who has this card equipped, has already triggered Watery Rebirth, then create 1 Curse of the Undercurrent on the opposing playing field.\nWhen Abyss Herald: Wicked Torrents, who has this card equipped, is defeated or triggers Watery Rebirth: Create 1 Curse of the Undercurrent on the opposing playing field.\n(You must have Abyss Herald: Wicked Torrents in your deck to add this card to your deck.)",  # noqa
                "zh-CN": "入场时：如果装备有此牌的深渊使徒·激流已触发过水之新生，则在对方场上生成暗流的诅咒。\n装备有此牌的深渊使徒·激流被击倒或触发水之新生时：在对方场上生成暗流的诅咒。\n（牌组中包含深渊使徒·激流，才能加入牌组）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Talent_InvokerHeraldWater.png",  # noqa
        "id": 222031,
    },
}


register_class(
    WateryRebirth_4_6
    | WateryRebirthHoned_4_6
    | AbyssHeraldWickedTorrents_4_6
    | CurseOfTheUndercurrent_4_6
    | RipplingBlades_4_6
    | SurgingUndercurrent_4_6,
    desc,
)
