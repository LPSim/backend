from typing import Any, List, Literal

from ....utils.class_registry import register_class

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


class MelodyLoop_3_3(AttackerSummonBase):
    name: Literal['Melody Loop'] = 'Melody Loop'
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


class GloriousSeason_3_3(SkillTalent):
    name: Literal['Glorious Season'] = 'Glorious Season'
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Barbara'] = 'Barbara'
    cost: Cost = Cost(
        elemental_dice_number = 4,
        elemental_dice_color = DieColor.HYDRO,
    )
    skill: Literal['Let the Show Begin♪'] = 'Let the Show Begin♪'
    usage: int = 1

    def event_handler_ROUND_PREPARE(
        self, match: Any, event_args: RoundPrepareEventArguments
    ) -> List[Actions]:
        """reset usage"""
        self.usage = 1
        return []

    def value_modifier_COST(
        self, value: CostValue, 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        Once per round, if summon "Melody Loop" is valid in our summon area,
        and our do switch, and have cost, then cost -1.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, no effect
            return value
        if self.usage <= 0:
            # no usage, no effect
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR == 0:
            # not switch charatctor, no effect
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player, no effect
            return value
        summons = match.player_tables[self.position.player_idx].summons
        have_summon = False
        for summon in summons:
            if summon.name == 'Melody Loop':
                have_summon = True
                break
        if not have_summon:
            # not have summon, no effect
            return value
        # decrease 1 any cost
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value


class GloriousSeason_4_2(GloriousSeason_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )


class Barbara_3_3(CharactorBase):
    name: Literal['Barbara']
    version: Literal['3.3'] = '3.3'
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


register_class(
    Barbara_3_3 | GloriousSeason_3_3 | GloriousSeason_4_2 | MelodyLoop_3_3
)
