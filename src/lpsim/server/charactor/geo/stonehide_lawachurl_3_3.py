from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import (
    AfterMakeDamageEventArguments, CharactorDefeatedEventArguments, 
)

from ...action import CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    CreateStatusPassiveSkill, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class UpaShato(ElementalBurstBase):
    name: Literal['Upa Shato'] = 'Upa Shato'
    damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 2
    )


class InfusedStonehide(CreateStatusPassiveSkill):
    name: Literal['Infused Stonehide'] = 'Infused Stonehide'
    status_name: Literal['Stonehide'] = 'Stonehide'


# Talents


class StonehideReforged_3_3(SkillTalent):
    name: Literal['Stonehide Reforged']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Stonehide Lawachurl'] = 'Stonehide Lawachurl'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: Literal['Upa Shato'] = 'Upa Shato'

    opposite_alive: List[int] = []

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Any
    ):
        """
        record enemy alive status
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, return
            return []
        # reset alive
        self.opposite_alive = []
        assert len(event.action.damage_value_list) > 0
        # if use skill, source of first should be self
        if not self.position.check_position_valid(
            event.action.damage_value_list[0].position, match,
            player_idx_same = True, charactor_idx_same = True,
            target_area = ObjectPositionType.SKILL
        ):
            # not self use skill, return
            return []
        for cid, charactor in enumerate(match.player_tables[
                1 - self.position.player_idx].charactors):
            self.opposite_alive.append(cid)
        return []

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If self is using skill, and enemy defeated, re-attach Stonehide and 
        Stone Force.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, return
            return []
        if event.action.player_idx == self.position.player_idx:
            # self defeated, return
            return []
        if event.action.charactor_idx not in self.opposite_alive:
            # defeated charactor not in opposite_alive, return
            return []
        # re-attach Stonehide and Stone Force
        return [
            CreateObjectAction(
                object_name = 'Stonehide',
                object_position = self.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS
                ),
                object_arguments = {}
            )
        ]


# charactor base


class StonehideLawachurl_3_3(CharactorBase):
    name: Literal['Stonehide Lawachurl']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.GEO
    max_hp: int = 8
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | UpaShato 
        | InfusedStonehide
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER,
        FactionType.HILICHURL
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Plama Lawa',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Movo Lawa',
                damage_type = DamageElementalType.PHYSICAL,
                cost = ElementalSkillBase.get_cost(self.element),
            ),
            UpaShato(),
            InfusedStonehide()
        ]


register_class(StonehideLawachurl_3_3 | StonehideReforged_3_3)
