from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DefendSummonBase

from ...modifiable_values import DamageIncreaseValue
from ...event import ReceiveDamageEventArguments, RoundPrepareEventArguments

from ...action import Actions, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class Ushi_3_6(DefendSummonBase):
    name: Literal['Ushi'] = 'Ushi'
    version: Literal['3.6'] = '3.6'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.GEO
    damage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = False

    create_status_triggered: bool = False

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If any of our charactor is attacked and not triggered, Arataki Itto
        gains Superlative Superstrength.
        """
        if self.create_status_triggered:
            # already triggered, no effect
            return []
        if (
            event.final_damage.target_position.player_idx 
            != self.position.player_idx
        ):
            # not attack our player, no effect
            return []
        if event.final_damage.damage_type != DamageType.DAMAGE:
            # not damage, no effect
            return []
        # trigger, gain Superlative Superstrength for first Arataki Itto
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if charactor.is_alive and charactor.name == 'Arataki Itto':
                # found alive itto, gain status
                status_position = charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS
                )
                self.create_status_triggered = True
                return [CreateObjectAction(
                    object_name = 'Superlative Superstrength',
                    object_position = status_position,
                    object_arguments = {}
                )]
        else:  # pragma: no cover
            # not found alive Itto, no effect
            return []


# Skills


class FightClubLegend(PhysicalNormalAttackBase):
    name: Literal['Fight Club Legend'] = 'Fight Club Legend'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 1,
        any_dice_number = 2,
    )


class MasatsuZetsugiAkaushiBurst(ElementalSkillBase):
    name: Literal[
        'Masatsu Zetsugi: Akaushi Burst!'] = 'Masatsu Zetsugi: Akaushi Burst!'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, create Ushi and create status
        """
        ret = super().get_actions(match)
        ret.append(self.create_summon('Ushi'))
        ret += [self.create_charactor_status('Superlative Superstrength')]
        return ret


class RoyalDescentBeholdIttoTheEvil(ElementalBurstBase):
    name: Literal[
        'Royal Descent: Behold, Itto the Evil!'
    ] = 'Royal Descent: Behold, Itto the Evil!'
    damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 3
    )
    version: Literal['3.6'] = '3.6'

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create status
        """
        return super().get_actions(match) + [
            self.create_charactor_status('Raging Oni King', {
                'version': self.version
            })
        ]


# Talents


class AratakiIchiban_3_6(SkillTalent):
    name: Literal['Arataki Ichiban']
    version: Literal['3.6'] = '3.6'
    charactor_name: Literal['Arataki Itto'] = 'Arataki Itto'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 1,
        any_dice_number = 2,
    )
    skill: Literal['Fight Club Legend'] = 'Fight Club Legend'


# charactor base


class AratakiItto_3_6(CharactorBase):
    name: Literal['Arataki Itto']
    version: Literal['3.6'] = '3.6'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        FightClubLegend | MasatsuZetsugiAkaushiBurst 
        | RoyalDescentBeholdIttoTheEvil
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    normal_attack_this_round: int = 0

    def _init_skills(self) -> None:
        self.skills = [
            FightClubLegend(),
            MasatsuZetsugiAkaushiBurst(),
            RoyalDescentBeholdIttoTheEvil(),
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        # reset normal attack counter
        self.normal_attack_this_round = 0
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, 
        match: Any, mode: Literal['TEST', 'REAL']
    ):
        """
        When use normal attack, add counter. 

        For the second time or more using normal attack this round,
        and is charged attack, and has status Superlative Superstrength,
        and equipped talent, add 1 damage.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not use normal attack
            return value
        # add counter
        self.normal_attack_this_round += 1
        if self.normal_attack_this_round <= 1:
            # first time, no effect
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, no effect
            return value
        status_found = False
        for status in self.status:
            if status.name == 'Superlative Superstrength':
                status_found = True
                break
        if not status_found:
            # not have status, no effect
            return value
        if self.talent is None:
            # not equipped talent, no effect
            return value
        # add damage
        value.damage += 1
        return value


register_class(
    AratakiItto_3_6 | AratakiIchiban_3_6 | Ushi_3_6
)
