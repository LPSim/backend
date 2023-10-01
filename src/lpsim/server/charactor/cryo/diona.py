from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import RoundEndEventArguments

from ...action import Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)
# Summons


class DrunkenMist(AttackerSummonBase):
    name: Literal['Drunken Mist'] = 'Drunken Mist'
    desc: str = (
        'End Phase: Deal 1 Cryo DMG, heal your active character for 2 HP.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[
            self.position.player_idx].get_active_charactor()
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = our_active.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        ))
        return ret


# Skills


class IcyPaws(ElementalSkillBase):
    name: Literal['Icy Paws'] = 'Icy Paws'
    desc: str = '''Deals 2 Cryo DMG, creates 1 Cat-Claw Shield.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        args = {}
        if self.is_talent_equipped(match):
            # have talent, shield gain one more usage
            args['usage'] = 2
            args['max_usage'] = 2
        return super().get_actions(match) + [
            self.create_team_status('Cat-Claw Shield', args)
        ]


class SignatureMix(ElementalBurstBase):
    name: Literal['Signature Mix'] = 'Signature Mix'
    desc: str = (
        'Deals 1 Cryo DMG, heals this character for 2 HP, summons 1 '
        'Drunken Mist.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        our_active = match.player_tables[
            self.position.player_idx].get_active_charactor()
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = our_active.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        ))
        ret.append(self.create_summon('Drunken Mist'))
        return ret


# Talents


class ShakenNotPurred(SkillTalent):
    name: Literal['Shaken, Not Purred']
    desc: str = (
        'Combat Action: When your active character is Diona, equip this card. '
        'After Diona equips this card, immediately use Icy Paws once. '
        'When your Diona, who has this card equipped, creates a Cat-Claw '
        'Shield, its Shield points +1.'
    )
    version: Literal['4.1'] = '4.1'
    charactor_name: Literal['Diona'] = 'Diona'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    skill: IcyPaws = IcyPaws()


# charactor base


class Diona(CharactorBase):
    name: Literal['Diona']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Kätzlein Cocktail" Diona'''
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | IcyPaws | SignatureMix
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.BOW
    talent: ShakenNotPurred | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Kätzlein Style',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            IcyPaws(),
            SignatureMix()
        ]
