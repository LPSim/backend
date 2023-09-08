from typing import Any, List, Literal

from ...event import (
    AfterMakeDamageEventArguments, CharactorDefeatedEventArguments, 
    GameStartEventArguments
)

from ...action import CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Skills


class UpaShato(ElementalBurstBase):
    name: Literal['Upa Shato'] = 'Upa Shato'
    desc: str = '''Deals 5 Physical DMG.'''
    damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 2
    )


class InfusedStonehide(PassiveSkillBase):
    name: Literal['Infused Stonehide'] = 'Infused Stonehide'
    desc: str = (
        '(Passive) When the battle begins, this character gains Stonehide '
        'and Stone Force.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain Stonehide
        """
        return [self.create_charactor_status('Stonehide')]


# Talents


class StonehideReforged(SkillTalent):
    name: Literal['Stonehide Reforged']
    desc: str = (
        'Combat Action: When your active character is Stonehide Lawachurl, '
        'equip this card. After Stonehide Lawachurl equips this card, '
        'immediately use Upa Shato once. When your Stonehide Lawachurl, who '
        'has this card equipped, defeats an opposing character: Stonehide '
        'Lawachurl will re-attach Stonehide and Stone Force.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Stonehide Lawachurl'] = 'Stonehide Lawachurl'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: UpaShato = UpaShato()

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
        return [self.skill.create_charactor_status('Stonehide')]


# charactor base


class StonehideLawachurl(CharactorBase):
    name: Literal['Stonehide Lawachurl']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Vale-Crosser" Stonehide Lawachurl'''
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
    talent: StonehideReforged | None = None

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
