from typing import Any, List, Literal, Tuple

from pydantic import PrivateAttr

from ....utils.class_registry import register_class

from ...summon.base import DefendSummonBase, AttackerSummonBase

from ...event import SkillEndEventArguments

from ...action import (
    Actions,
    ChangeObjectUsageAction,
    ChargeAction,
    CreateRandomObjectAction,
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    SkillBase,
    SkillTalent,
)


# Summons


class Squirrel_3_3(AttackerSummonBase):
    name: Literal["Oceanic Mimic: Squirrel"] = "Oceanic Mimic: Squirrel"
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2


class Raptor_3_3(AttackerSummonBase):
    name: Literal["Oceanic Mimic: Raptor"] = "Oceanic Mimic: Raptor"
    version: Literal["3.3"] = "3.3"
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1


class Frog_3_3(DefendSummonBase):
    name: Literal["Oceanic Mimic: Frog"] = "Oceanic Mimic: Frog"
    version: Literal["3.3"] = "3.3"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = True


# Skills


mimic_names = [
    "Oceanic Mimic: Squirrel",
    "Oceanic Mimic: Frog",
    "Oceanic Mimic: Raptor",
]


class RhodeiaElementSkill(ElementalSkillBase):
    name: Literal["Oceanid Mimic Summoning", "The Myriad Wilds"]
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3)
    _summon_number: int = PrivateAttr(1)
    version: Literal["3.3"] = "3.3"

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Oceanid Mimic Summoning":
            pass
        else:
            assert self.name == "The Myriad Wilds"
            self._summon_number = 2
            self.cost.elemental_dice_number = 5

    def _get_exist_unexist_names(self, match: Any) -> Tuple[List[str], List[str]]:
        """
        Create two lists including exist and unexist names.
        """
        summons = match.player_tables[self.position.player_idx].summons
        summon_names = [x.name for x in summons]
        unexist_names: List[str] = []
        exist_names: List[str] = []
        for name in mimic_names:
            if name not in summon_names:
                unexist_names.append(name)
            else:
                exist_names.append(name)
        return exist_names, unexist_names

    def get_actions(self, match: Any) -> List[ChargeAction | CreateRandomObjectAction]:
        """
        create object
        """
        exist_names, unexist_names = self._get_exist_unexist_names(match)
        ret: List[ChargeAction | CreateRandomObjectAction] = []
        target_position = ObjectPosition(
            player_idx=self.position.player_idx, area=ObjectPositionType.SUMMON, id=-1
        )
        if len(unexist_names) == 0:
            # all exist, only from exist
            ret.append(
                CreateRandomObjectAction(
                    object_names=exist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number,
                )
            )
        elif len(unexist_names) >= self._summon_number:
            # enough unexist
            ret.append(
                CreateRandomObjectAction(
                    object_names=unexist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number,
                )
            )
        else:
            # not enough unexist, create all unexist and refresh random exist
            ret.append(
                CreateRandomObjectAction(
                    object_names=unexist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=len(unexist_names),
                )
            )
            ret.append(
                CreateRandomObjectAction(
                    object_names=exist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number - len(unexist_names),
                )
            )
        ret.append(self.charge_self(1))
        return ret


class TideAndTorrent(ElementalBurstBase):
    name: Literal["Tide and Torrent"] = "Tide and Torrent"
    damage: int = 2
    damage_per_summon: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3, charge=3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        summons = match.player_tables[self.position.player_idx].summons
        self.damage += len(summons) * self.damage_per_summon
        ret = super().get_actions(match)
        self.damage -= len(summons) * self.damage_per_summon
        return ret


# Talents


class StreamingSurge_3_3(SkillTalent):
    name: Literal["Streaming Surge"]
    version: Literal["3.3"] = "3.3"
    character_name: Literal["Rhodeia of Loch"] = "Rhodeia of Loch"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=4, charge=3
    )
    skill: Literal["Tide and Torrent"] = "Tide and Torrent"

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        When equipped and this character use burst, change all summons' usage
        by 1.
        """
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            source_area=ObjectPositionType.CHARACTER,
            target_area=ObjectPositionType.SKILL,
        ):
            # not equipped, or not self use skill, or not skill
            return []
        skill: SkillBase = match.get_object(event.action.position)
        if skill.skill_type != SkillType.ELEMENTAL_BURST:
            # not elemental burst
            return []
        summons = match.player_tables[self.position.player_idx].summons
        ret = []
        for summon in summons:
            ret.append(
                ChangeObjectUsageAction(object_position=summon.position, change_usage=1)
            )
        return ret


# character base


class RhodeiaOfLoch_3_3(CharacterBase):
    name: Literal["Rhodeia of Loch"]
    version: Literal["3.3"] = "3.3"
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[ElementalNormalAttackBase | RhodeiaElementSkill | TideAndTorrent] = []
    faction: List[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Surge",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            RhodeiaElementSkill(
                name="Oceanid Mimic Summoning",
            ),
            RhodeiaElementSkill(
                name="The Myriad Wilds",
            ),
            TideAndTorrent(),
        ]


register_class(
    RhodeiaOfLoch_3_3 | Squirrel_3_3 | Raptor_3_3 | Frog_3_3 | StreamingSurge_3_3
)
