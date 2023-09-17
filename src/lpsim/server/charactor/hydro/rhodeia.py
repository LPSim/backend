from typing import Any, List, Literal

from ...summon.base import DefendSummonBase, AttackerSummonBase

from ...event import SkillEndEventArguments

from ...action import (
    ActionTypes, Actions, ChangeObjectUsageAction, ChargeAction, 
    CreateObjectAction
)
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillBase, SkillTalent
)


# Summons


class Squirrel(AttackerSummonBase):
    name: Literal['Oceanic Mimic: Squirrel'] = 'Oceanic Mimic: Squirrel'
    desc: str = '''End Phase: Deal 2 Hydro DMG. Usage(s): 2'''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2


class Raptor(AttackerSummonBase):
    name: Literal['Oceanic Mimic: Raptor'] = 'Oceanic Mimic: Raptor'
    desc: str = '''End Phase: Deal 1 Hydro DMG. Usage(s): 3'''
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1


class Frog(DefendSummonBase):
    name: Literal['Oceanic Mimic: Frog'] = 'Oceanic Mimic: Frog'
    desc: str = (
        'When your active character takes DMG: Decrease DMG taken by 1. '
        'When the Usages are depleted, this card will not be discarded. '
        'At the End Phase, if Usage(s) have been depleted: Discard this card, '
        'deal 2 Hydro DMG. Usage(s): 2'
    )
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
    desc: str = (
        'Randomly summons XX Oceanid Mimic (Prioritizes summoning a different '
        'type from preexisting ones).'
    )
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    summon_number: int = 1

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == 'Oceanid Mimic Summoning':
            pass
        else:
            assert self.name == 'The Myriad Wilds'
            self.summon_number = 2
            self.cost.elemental_dice_number = 5
        self.desc = self.desc.replace('XX', str(self.summon_number))

    def get_next_summon_names(
        self, match: Any, number: int
    ) -> List[int]:
        """
        Get next summon names randomly, but fit the rule that try to avoid
        summoning the same type.
        """
        summons = match.player_tables[self.position.player_idx].summons
        summon_names = [x.name for x in summons]
        select_idx = []
        for idx, name in enumerate(mimic_names):
            if name not in summon_names:
                select_idx.append(idx)
        if len(select_idx) > number:
            match._random_shuffle(select_idx)
            select_idx = select_idx[:number]
        elif len(select_idx) < number:
            other_idx = [x for x in range(len(mimic_names)) 
                         if x not in select_idx]
            match._random_shuffle(other_idx)
            select_idx += other_idx[:number - len(select_idx)]
        else:
            if len(select_idx) > 1:
                match._random_shuffle(select_idx)
        return select_idx

    def get_actions(
            self, match: Any) -> List[ChargeAction | CreateObjectAction]:
        """
        create object
        """
        name_idxs = self.get_next_summon_names(match, self.summon_number)
        ret: List[ChargeAction | CreateObjectAction] = []
        for idx in name_idxs:
            ret.append(self.create_summon(mimic_names[idx]))
        ret.append(self.charge_self(1))
        return ret


class TideAndTorrent(ElementalBurstBase):
    name: Literal['Tide and Torrent'] = 'Tide and Torrent'
    desc: str = (
        'Deals 2 Hydro DMG. For each friendly Summon on the field, '
        'deals +2 additional DMG.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        summons = match.player_tables[self.position.player_idx].summons
        assert ret[-1].type == ActionTypes.MAKE_DAMAGE
        ret[-1].damage_value_list[0].damage += len(summons) * 2
        return ret


# Talents


class StreamingSurge(SkillTalent):
    name: Literal['Streaming Surge']
    desc: str = (
        'Combat Action: When your active character is Rhodeia of Loch, '
        'equip this card. After Rhodeia of Loch equips this card, '
        'immediately use Tide and Torrent once. When your Rhodeia of Loch, '
        'who has this card equipped, uses Tide and Torrent, all of your '
        'Summon(s) gain +1 Usage(s).'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Rhodeia of Loch'] = 'Rhodeia of Loch'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
        charge = 3
    )
    skill: TideAndTorrent = TideAndTorrent()

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
                change_type = 'DELTA',
                change_usage = 1
            ))
        return ret


# charactor base


class RhodeiaOfLoch(CharactorBase):
    name: Literal['Rhodeia of Loch']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Lady of Clear Waters" Rhodeia'''
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
    talent: StreamingSurge | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Surge',
                damage_type = self.element,
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
