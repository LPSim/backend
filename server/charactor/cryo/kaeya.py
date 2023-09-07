from typing import Any, List, Literal

from ...event import RoundPrepareEventArguments, SkillEndEventArguments

from ...action import Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class Frostgnaw(ElementalSkillBase):
    name: Literal['Frostgnaw'] = 'Frostgnaw'
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = ElementalSkillBase.get_cost(ElementType.CRYO)


class GlacialWaltz(ElementalBurstBase):
    name: Literal['Glacial Waltz'] = 'Glacial Waltz'
    desc: str = '''Deals 1 Cryo DMG, creates 1 Icicle.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status('Icicle')
        ]


# Talents


class ColdBloodedStrike(SkillTalent):
    name: Literal['Cold-Blooded Strike']
    desc: str = (
        'Combat Action: When your active character is Kaeya, equip this card. '
        'After Kaeya equips this card, immediately use Frostgnaw once. '
        'After your Kaeya, who has this card equipped, uses Frostgnaw, '
        'he heals himself for 2 HP. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Kaeya'] = 'Kaeya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4,
    )
    skill: Frostgnaw = Frostgnaw()
    usage: int = 1

    def equip(self, match: Any) -> List[Actions]:
        """
        Reset usage
        """
        self.usage = 1
        return super().equip(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset Usage
        """
        self.usage = 1
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When attached charactor use elemental skill, then heal itself.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR,
        ):
            # not same player or charactor, or not skill, or not equipped
            return []
        if self.usage <= 0:
            # out of usage
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        skill = charactor.get_object(event.action.position)
        assert skill is not None
        if skill.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        # heal itself
        self.usage -= 1
        return [self.skill.heal_self(match, 2)]


# charactor base


class Kaeya(CharactorBase):
    name: Literal['Kaeya']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Frostwind Swordsman" Kaeya'''
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Frostgnaw | GlacialWaltz
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: ColdBloodedStrike | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Ceremonial Bladework',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Frostgnaw(),
            GlacialWaltz(),
        ]
