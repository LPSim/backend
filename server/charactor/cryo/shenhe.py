from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageIncreaseValue

from ...action import Actions
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


class TalismanSpirit(AttackerSummonBase):
    name: Literal['Talisman Spirit'] = 'Talisman Spirit'
    desc: str = (
        'End Phase: Deal 1 Cryo DMG. '
        'When this Summon is on the field: Opposing character(s) take +1 '
        'Cryo DMG and Physical DMG.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        When enemy receives physical or cryo damage, regardless of source,
        increase damage by 1
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, do nothing
            return value
        if value.target_position.player_idx == self.position.player_idx:
            # attack self, no nothing
            return value
        if value.damage_elemental_type not in [
            DamageElementalType.CRYO, DamageElementalType.PHYSICAL
        ]:
            # not cryo or physical, do nothing
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


# Skills


class SpringSpiritSummoning(ElementalSkillBase):
    name: Literal['Spring Spirit Summoning'] = 'Spring Spirit Summoning'
    desc: str = '''Deals 2 Cryo DMG, creates 1 Icy Quill.'''
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
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.talent is not None:
            args = {
                'talent_usage': 1,
                'talent_max_usage': 1,
            }
        return super().get_actions(match) + [
            self.create_team_status('Icy Quill', args),
        ]


class DivineMaidensDeliverance(ElementalBurstBase):
    name: Literal[
        "Divine Maiden's Deliverance"] = "Divine Maiden's Deliverance"
    desc: str = '''Deals 1 Cryo DMG, summons 1 Talisman Spirit'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Talisman Spirit')
        ]


# Talents


class MysticalAbandon(SkillTalent):
    name: Literal['Mystical Abandon'] = 'Mystical Abandon'
    desc: str = (
        'Combat Action: When your active character is Shenhe, equip this card.'
        'After Shenhe equips this card, immediately use Spring Spirit '
        'Summoning once. When the Icy Quill created by your Shenhe, who has '
        "this card equipped, is triggered by your characters' Normal Attacks, "
        'its Usages will not decrease. (Once per Round)'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Shenhe'] = 'Shenhe'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    skill: SpringSpiritSummoning = SpringSpiritSummoning()


# charactor base


class Shenhe(CharactorBase):
    name: Literal['Shenhe']
    version: Literal['3.7'] = '3.7'
    desc: str = '''"Lonesome Transcendence" Shenhe'''
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | SpringSpiritSummoning | DivineMaidensDeliverance
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: MysticalAbandon | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Dawnstar Piercer',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SpringSpiritSummoning(),
            DivineMaidensDeliverance(),
        ]
