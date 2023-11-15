from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import CreateObjectEventArguments, RoundPrepareEventArguments

from ...summon.base import AttackerSummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class CuileinAnbar_3_3(AttackerSummonBase):
    name: Literal['Cuilein-Anbar'] = 'Cuilein-Anbar'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 2


# Skills


class FloralBrush(ElementalSkillBase):
    name: Literal['Floral Brush'] = 'Floral Brush'
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
    )
    create_status_counter: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        In prepare, reset counter
        """
        self.create_status_counter = 0
        return []

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        If our charactor create Floral Sidewinder, increase create status
        """
        if event.action.object_position.player_idx != self.position.player_idx:
            # not our charactor
            return []
        if event.action.object_name != 'Floral Sidewinder':
            # not Floral Sidewinder
            return []
        self.create_status_counter += 1
        return []

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If talent equipped, before attack, create status.
        """
        ret = super().get_actions(match)
        if self.create_status_counter > 0:
            # created this round, not create
            return ret
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.talent is None:
            # no talent equipped
            return ret
        ret = [self.create_team_status('Floral Sidewinder')] + ret
        return ret


class TrumpCardKitty(ElementalBurstBase):
    name: Literal['Trump-Card Kitty'] = 'Trump-Card Kitty'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('Cuilein-Anbar')
        ]


# Talents


class FloralSidewinder_3_4(SkillTalent):
    """
    Because before using skill, the status should appear, and status need to
    listen DAMAGE_RECEIVE event, we should modify both actions of 
    elemental skill and equipping this card.
    """
    name: Literal['Floral Sidewinder']
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Collei'] = 'Collei'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 4
    )
    skill: Literal['Floral Brush'] = 'Floral Brush'


class FloralSidewinder_3_3(FloralSidewinder_3_4):
    version: Literal['3.3']
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )


# charactor base


class Collei_3_3(CharactorBase):
    name: Literal['Collei']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | FloralBrush | TrumpCardKitty
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = "Supplicant's Bowmanship",
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            FloralBrush(),
            TrumpCardKitty()
        ]


register_class(
    Collei_3_3 | FloralSidewinder_3_3 | FloralSidewinder_3_4 | CuileinAnbar_3_3
)
