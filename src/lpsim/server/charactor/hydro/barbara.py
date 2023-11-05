from typing import Any, List, Literal

from ..old_version.talent_cards_4_2 import GloriousSeason_3_3

from ...summon.base import AttackerSummonBase

from ...modifiable_values import CostValue, DamageValue
from ...event import RoundEndEventArguments, RoundPrepareEventArguments

from ...action import (
    Actions, MakeDamageAction
)
from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DamageType, DieColor, ElementType, 
    FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


class MelodyLoop(AttackerSummonBase):
    name: Literal['Melody Loop'] = 'Melody Loop'
    desc: str = (
        'End Phase: Heal all your characters for 1 HP and your active '
        'character gains Hydro Application. '
        'Usage(s): 2'
    )
    version: Literal['3.3'] = '3.3'
    damage_elemental_type: DamageElementalType = DamageElementalType.HEAL
    damage: int = -1
    usage: int = 2
    max_usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        player_idx = self.position.player_idx
        assert self.usage > 0
        self.usage -= 1
        target_table = match.player_tables[player_idx]
        damage_action = MakeDamageAction(
            damage_value_list = [],
        )
        for cid, charactor in enumerate(target_table.charactors):
            if charactor.is_alive:
                damage_action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = self.damage,
                        damage_elemental_type 
                        = self.damage_elemental_type,
                        cost = Cost(),
                    )
                )
            if target_table.active_charactor_idx == cid:
                assert charactor.is_alive
                damage_action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.ELEMENT_APPLICATION,
                        target_position = charactor.position,
                        damage = 0,
                        damage_elemental_type
                        = DamageElementalType.HYDRO,
                        cost = Cost(),
                    )
                )
        return [damage_action]


class LetTheShowBegin(ElementalSkillBase):
    name: Literal['Let the Show Begin♪'] = 'Let the Show Begin♪'
    desc: str = (
        'Deals 1 Hydro DMG, summons 1 Melody Loop.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.HYDRO
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_summon('Melody Loop'))
        return ret


class ShiningMiracle(ElementalBurstBase):
    name: Literal['Shining Miracle'] = 'Shining Miracle'
    desc: str = '''Heals all of your characters for 4 HP.'''
    damage: int = -4
    damage_type: DamageElementalType = DamageElementalType.HEAL
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.HYDRO,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = [self.charge_self(-3)]
        charactors = match.player_tables[self.position.player_idx].charactors
        heal_action = MakeDamageAction(
            damage_value_list = [],
        )
        for charactor in charactors:
            if charactor.is_alive:
                heal_action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_type,
                        cost = self.cost.copy(),
                    )
                )
        ret.append(heal_action)
        return ret


class GloriousSeason(GloriousSeason_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )


class Barbara(CharactorBase):
    name: Literal['Barbara']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Shining Idol" Barbara'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase | LetTheShowBegin | ShiningMiracle
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: GloriousSeason | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Whisper of Water',
                damage_type = DamageElementalType.HYDRO,
                cost = ElementalNormalAttackBase.get_cost(
                    ElementType.HYDRO
                )
            ),
            LetTheShowBegin(),
            ShiningMiracle(),
        ]
