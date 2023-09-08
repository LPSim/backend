from typing import Any, List, Literal

from ...event import MakeDamageEventArguments, SkillEndEventArguments

from ...summon.base import SwirlChangeSummonBase

from ...action import (
    Actions, CreateObjectAction, SwitchCharactorAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, ElementalReactionType, 
    FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class AutumnWhirlwind(SwirlChangeSummonBase):
    name: Literal['Autumn Whirlwind'] = 'Autumn Whirlwind'
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 3
    damage: int = 1


# Skills


class Chihayaburu(ElementalSkillBase):
    name: Literal['Chihayaburu'] = 'Chihayaburu'
    desc: str = (
        'Deals 3 Anemo DMG, attaches Midare Ranzan to this character. If this '
        'skill triggers Swirl, Midare Ranzan is converted to the '
        'Swirled Element. After the Skill DMG is finalized: Your team '
        'switches to the next character.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = [
            self.charge_self(1),
            # create status first, so it can change element
            self.create_charactor_status('Midare Ranzan: New'),
        ]
        # make damage
        ret.append(self.attack_opposite_active(
            match, self.damage, self.damage_type))
        # switch charactor
        next_charactor = match.player_tables[
            self.position.player_idx].next_charactor_idx()
        if next_charactor is not None:
            ret.append(
                SwitchCharactorAction(
                    player_idx = self.position.player_idx,
                    charactor_idx = next_charactor,
                )
            )
        return ret


class KazuhaSlash(ElementalBurstBase):
    name: Literal['Kazuha Slash'] = 'Kazuha Slash'
    desc: str = '''Deals 3 Anemo DMG, summons 1 Autumn Whirlwind.'''
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return [
            self.charge_self(1),
            self.create_summon('Autumn Whirlwind'),
            self.attack_opposite_active(match, self.damage, self.damage_type)
        ]


# Talents


class PoeticsOfFuubutsu(SkillTalent):
    name: Literal['Poetics of Fuubutsu']
    desc: str = (
        'Combat Action: When your active character is Kaedehara Kazuha, equip '
        'this card. After Kaedehara Kazuha equips this card, immediately use '
        'Chihayaburu once. After Kaedehara Kazuha triggers Swirl with this '
        'card equipped: For the next 2 instances, your Characters and Summons '
        'will deal +1 DMG for the Elemental Type Swirled. (Each Elemental '
        'Type is counted independently)'
    )
    version: Literal['3.8'] = '3.8'
    charactor_name: Literal['Kaedehara Kazuha'] = 'Kaedehara Kazuha'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
    )
    skill: Chihayaburu = Chihayaburu()

    swirl_element = ElementType.NONE

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        when damage made, if it is from kazuha, and has swirl, record element.
        """
        for damage in event.damages:
            if not self.position.check_position_valid(
                damage.final_damage.position, match, 
                player_idx_same = True, charactor_idx_same = True, 
                target_area = ObjectPositionType.SKILL,
            ):
                # not self charactor use skill, do nothing
                continue
            if damage.final_damage.damage_from_element_reaction:
                # damage from elemental reaction, do nothing
                continue
            if damage.elemental_reaction != ElementalReactionType.SWIRL:
                # not swirl, do nothing
                continue
            assert self.swirl_element == ElementType.NONE, (
                'element type already determined'
            )
            # swirl, change element type
            elements = damage.reacted_elements
            assert elements[0] == ElementType.ANEMO, 'First must be anemo'
            self.swirl_element = elements[1]
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If kazuha did skill and swirled, generate Poetics of Fuubutsu with
        corresponding element.
        """
        element = self.swirl_element
        # regardless of skill situation, reset swirl element
        self.swirl_element = ElementType.NONE
        if element == ElementType.NONE:
            # no swirl, do nothing
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR,
        ):  # pragma: no cover
            # not same player or charactor, or not skill, or not equipped
            return []
        # this charactor swirl, generate Poetics of Fuubutsu
        return [CreateObjectAction(
            object_name = f'{self.name}: {element.name.capitalize()}',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = 0,
            ),
            object_arguments = {}
        )]


# charactor base


class KaedeharaKazuha(CharactorBase):
    name: Literal['Kaedehara Kazuha']
    version: Literal['3.8'] = '3.8'
    desc: str = '''Scarlet Leaves Pursue Wild Waves: Kaedehara Kazuha'''
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Chihayaburu | KazuhaSlash
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: PoeticsOfFuubutsu | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Garyuu Bladework',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Chihayaburu(),
            KazuhaSlash()
        ]
