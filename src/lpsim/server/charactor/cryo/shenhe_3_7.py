from typing import Any, List, Literal

from ....utils.class_registry import register_class

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


class TalismanSpirit_3_7(AttackerSummonBase):
    name: Literal['Talisman Spirit'] = 'Talisman Spirit'
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
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    max_usage: int = 3

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        args = {
            'usage': self.max_usage,
            'max_usage': self.max_usage,
        }
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.talent is not None:
            args.update({
                'talent_usage': 1,
                'talent_max_usage': 1,
            })
        return super().get_actions(match) + [
            self.create_team_status('Icy Quill', args),
        ]


class DivineMaidensDeliverance(ElementalBurstBase):
    name: Literal[
        "Divine Maiden's Deliverance"] = "Divine Maiden's Deliverance"
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


class MysticalAbandon_3_7(SkillTalent):
    name: Literal['Mystical Abandon'] = 'Mystical Abandon'
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Shenhe'] = 'Shenhe'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    skill: Literal['Spring Spirit Summoning'] = 'Spring Spirit Summoning'


# charactor base


class Shenhe_3_7(CharactorBase):
    name: Literal['Shenhe']
    version: Literal['3.7'] = '3.7'
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

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Dawnstar Piercer',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SpringSpiritSummoning(),
            DivineMaidensDeliverance(),
        ]


register_class(Shenhe_3_7 | MysticalAbandon_3_7 | TalismanSpirit_3_7)
