from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DefendSummonBase, AttackerSummonBase

from ...event import SkillEndEventArguments

from ...action import (
    Actions, ChangeObjectUsageAction, ChargeAction, CreateObjectAction
)
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillBase, SkillTalent
)


# Summons


class Squirrel_3_3(AttackerSummonBase):
    name: Literal['Oceanic Mimic: Squirrel'] = 'Oceanic Mimic: Squirrel'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2


class Raptor_3_3(AttackerSummonBase):
    name: Literal['Oceanic Mimic: Raptor'] = 'Oceanic Mimic: Raptor'
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1


class Frog_3_3(DefendSummonBase):
    name: Literal['Oceanic Mimic: Frog'] = 'Oceanic Mimic: Frog'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = True


# Skills


mimic_names = [
    'Oceanic Mimic: Squirrel',
    'Oceanic Mimic: Frog',
    'Oceanic Mimic: Raptor'
]


class RhodeiaElementSkill(ElementalSkillBase):
    name: Literal['Oceanid Mimic Summoning',
                  'The Myriad Wilds']
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    summon_number: int = 1
    version: Literal['3.3'] = '3.3'

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == 'Oceanid Mimic Summoning':
            pass
        else:
            assert self.name == 'The Myriad Wilds'
            self.summon_number = 2
            self.cost.elemental_dice_number = 5

    def get_next_summon_names(
        self, match: Any, occupied: List[int]
    ) -> int:
        """
        Get next summon names randomly, but fit the rule that try to avoid
        summoning the same type.
        """
        summons = match.player_tables[self.position.player_idx].summons
        summon_names = [x.name for x in summons]
        select_idx = []
        for idx, name in enumerate(mimic_names):
            if name not in summon_names and idx not in occupied:
                select_idx.append(idx)
        if len(select_idx) == 0:
            # all exist, get one from not occupied
            select_idx = [x for x in range(3) if x not in occupied]
        if match.config.recreate_mode:
            """
            in recreate mode, the number should always be 1. read name from
            config.

            the key in information is `rhodeia`, name can be one of three
            summons, and can use short names (i.e. frog, raptor, squirrel).
            """
            sname = match.config.random_object_information['rhodeia'].pop(0)
            s_idx = -1
            for idx, name in enumerate(mimic_names):
                if sname.lower() in name.lower():
                    s_idx = idx
                    break
            else:
                raise AssertionError(f'Unknown summon name {sname}')
            assert s_idx in select_idx
            return s_idx
        return select_idx[int(match._random() * len(select_idx))]

    def get_actions(
            self, match: Any) -> List[ChargeAction | CreateObjectAction]:
        """
        create object
        """
        name_idxs = []
        for _ in range(self.summon_number):
            name_idxs.append(self.get_next_summon_names(match, name_idxs))
        ret: List[ChargeAction | CreateObjectAction] = []
        for idx in name_idxs:
            ret.append(self.create_summon(
                mimic_names[idx], { 'version': self.version }
            ))
        ret.append(self.charge_self(1))
        return ret


class TideAndTorrent(ElementalBurstBase):
    name: Literal['Tide and Torrent'] = 'Tide and Torrent'
    damage: int = 2
    damage_per_summon: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        summons = match.player_tables[self.position.player_idx].summons
        self.damage += len(summons) * self.damage_per_summon
        ret = super().get_actions(match)
        self.damage -= len(summons) * self.damage_per_summon
        return ret


# Talents


class StreamingSurge_3_3(SkillTalent):
    name: Literal['Streaming Surge']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Rhodeia of Loch'] = 'Rhodeia of Loch'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
        charge = 3
    )
    skill: Literal['Tide and Torrent'] = 'Tide and Torrent'

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments,
        match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        When equipped and this charactor use burst, change all summons' usage
        by 1.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL,
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
            ret.append(ChangeObjectUsageAction(
                object_position = summon.position,
                change_usage = 1
            ))
        return ret


# charactor base


class RhodeiaOfLoch_3_3(CharactorBase):
    name: Literal['Rhodeia of Loch']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase
        | RhodeiaElementSkill | TideAndTorrent
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Surge',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            RhodeiaElementSkill(
                name = 'Oceanid Mimic Summoning',
            ),
            RhodeiaElementSkill(
                name = 'The Myriad Wilds',
            ),
            TideAndTorrent(),
        ]


register_class(
    RhodeiaOfLoch_3_3 | Squirrel_3_3 | Raptor_3_3 | Frog_3_3
    | StreamingSurge_3_3
)
