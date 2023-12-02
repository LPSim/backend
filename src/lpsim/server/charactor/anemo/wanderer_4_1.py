from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import CostValue, DamageValue
from ...event import SkillEndEventArguments, SwitchCharactorEventArguments

from ...action import (
    ActionTypes, Actions, ChangeObjectUsageAction, MakeDamageAction, 
    RemoveObjectAction
)
from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DamageType, 
    DieColor, ElementType, FactionType, ObjectPositionType, SkillType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class YuubanMeigen(ElementalNormalAttackBase):
    name: Literal['Yuuban Meigen'] = 'Yuuban Meigen'
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = ElementalNormalAttackBase.get_cost(ElementType.ANEMO)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        if self has Windfavored, then deal 2 more damage and attack next
        charactor.
        """
        windfavored = None
        this_charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        for status in this_charactor.status:
            if status.name == 'Windfavored':
                assert status.usage >= 1
                windfavored = status
                break
        if windfavored is None:
            # do normal attack
            return super().get_actions(match)
        self.damage = 3
        # increase damage, and attack next charactor
        ret = super().get_actions(match)
        self.damage = 1
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        enemy_table = match.player_tables[1 - self.position.player_idx]
        next = enemy_table.next_charactor_idx()
        if next is not None:
            # modify attack target
            damage_action.damage_value_list[
                0].target_position = enemy_table.charactors[next].position
        assert len(ret) == 2
        return [damage_action, ret[1], ChangeObjectUsageAction(
            object_position = windfavored.position,
            change_usage = -1
        )]


class HanegaSongOfTheWind(ElementalSkillBase):
    name: Literal['Hanega: Song of the Wind'] = 'Hanega: Song of the Wind'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_charactor_status('Windfavored'),
        ]


class KyougenFiveCeremonialPlays(ElementalBurstBase):
    name: Literal[
        'Kyougen: Five Ceremonial Plays'] = 'Kyougen: Five Ceremonial Plays'
    damage: int = 7
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        windfavored = None
        this_charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        for status in this_charactor.status:
            if status.name == 'Windfavored':
                assert status.usage >= 1
                windfavored = status
                break
        if windfavored is not None:
            self.damage = 8
            ret = [
                RemoveObjectAction(
                    object_position = windfavored.position
                )
            ] + super().get_actions(match)
            self.damage = 7
            return ret
        return super().get_actions(match)


# Talents


class GalesOfReverie_4_1(SkillTalent):
    name: Literal['Gales of Reverie']
    version: Literal['4.1'] = '4.1'
    charactor_name: Literal['Wanderer'] = 'Wanderer'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
    )
    skill: Literal['Hanega: Song of the Wind'] = 'Hanega: Song of the Wind'

    usage: int = 0
    switch_performed: bool = False

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self use normal attack, and has Windfavored, and is charged attack,
        mark talent activated.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self do skill, or not equipped
            return []
        if not (
            event.action.skill_type == SkillType.NORMAL_ATTACK
            and match.player_tables[self.position.player_idx].charge_satisfied
        ):
            # not charged attack
            return []
        this_charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        for status in this_charactor.status:
            if status.name == 'Windfavored':
                # found windfavored, set card usage to 1
                self.usage = 1
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        If self has usage, reduce switch charactor cost from this charactor
        by 1
        """
        if self.usage <= 0:
            # not activated
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not this player, nor not equipped
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR.value == 0:
            # not switch charactor
            return value
        # reduce 1 cost
        value.cost.decrease_cost(None)
        if mode == 'REAL':
            # mark switch performed and decrease usage
            self.usage = 0
            self.switch_performed = True
        return value

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self has usage and switch from this charactor, make 1 anemo damage
        and decrease usage.
        """
        if not self.switch_performed:
            # not switch performed
            return []
        self.switch_performed = False
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    target_position = target.position,
                    damage = 1,
                    damage_type = DamageType.DAMAGE,
                    damage_elemental_type = DamageElementalType.ANEMO,
                    cost = Cost(),
                )
            ]
        )]


# charactor base


class Wanderer_4_1(CharactorBase):
    name: Literal['Wanderer']
    version: Literal['4.1'] = '4.1'
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        YuubanMeigen | HanegaSongOfTheWind | KyougenFiveCeremonialPlays
    ] = []
    faction: List[FactionType] = []
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            YuubanMeigen(),
            HanegaSongOfTheWind(),
            KyougenFiveCeremonialPlays(),
        ]


register_class(Wanderer_4_1 | GalesOfReverie_4_1)
