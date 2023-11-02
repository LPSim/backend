from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import MakeDamageEventArguments, RoundEndEventArguments

from ...action import ActionTypes, Actions, CreateDiceAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, ELEMENT_TO_DIE_COLOR, DamageElementalType, 
    DamageType, DieColor, ElementType, FactionType, ObjectPositionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class GossamerSprite(AttackerSummonBase):
    name: Literal['Gossamer Sprite'] = 'Gossamer Sprite'
    desc: str = (
        'End Phase: Deal 1 Dendro DMG, heal your active character for 1 HP.'
    )
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        make_damage_action = ret[-1]
        assert make_damage_action.type == ActionTypes.MAKE_DAMAGE
        make_damage_action.damage_value_list.append(DamageValue(
            position = self.position,
            damage_type = DamageType.HEAL,
            target_position = active_charactor.position,
            damage = -1,
            damage_elemental_type = DamageElementalType.HEAL,
            cost = Cost(),
        ))
        return ret


# Skills


class UniversalDiagnosis(ElementalSkillBase):
    name: Literal['Universal Diagnosis'] = 'Universal Diagnosis'
    desc: str = '''Deals 1 Dendro DMG, summons 1 Gossamer Sprite.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('Gossamer Sprite')]


class HolisticRevivification(ElementalBurstBase):
    name: Literal['Holistic Revivification'] = 'Holistic Revivification'
    desc: str = '''Creates 1 Pulsing Clarity and Seamless Shield.'''
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return [
            self.charge_self(-2),
            self.create_team_status('Pulsing Clarity'),
            self.create_team_status('Seamless Shield'),
        ]


# Talents


class AllThingsAreOfTheEarth(SkillTalent):
    name: Literal['All Things Are of the Earth']
    desc: str = (
        'Combat Action: When your active character is Baizhu, equip this '
        'card. After Baizhu equips this card, immediately use Holistic '
        'Revivification once. When your Baizhu, who has this card equipped, '
        'is on the field, when Seamless Shield activates a healing effect, '
        'generate 1 Elemental Dice of the same type as your active character.'
    )
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Baizhu'] = 'Baizhu'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: HolisticRevivification = HolisticRevivification()

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When heal made by our shield, create one dice
        """
        source_position = event.action.damage_value_list[0].position
        if (
            self.position.area != ObjectPositionType.CHARACTOR
            or source_position.area != ObjectPositionType.TEAM_STATUS
            or source_position.player_idx != self.position.player_idx
        ):
            # not our team status, or not equipped
            return []
        source = match.get_object(source_position)
        if source.name != 'Seamless Shield':
            # not our shield
            return []
        # create dice
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = ELEMENT_TO_DIE_COLOR[active_charactor.element],
                number = 1,
            )
        ]


# charactor base


class Baizhu(CharactorBase):
    name: Literal['Baizhu']
    version: Literal['4.2'] = '4.2'
    desc: str = '''"Beyond Mortality" Baizhu'''
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | UniversalDiagnosis | HolisticRevivification
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: AllThingsAreOfTheEarth | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'The Classics of Acupuncture',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            UniversalDiagnosis(),
            HolisticRevivification(),
        ]
