from typing import Any, List, Literal

from ...summon.base import SwirlChangeSummonBase

from ...modifiable_values import DamageIncreaseValue

from ...action import ActionTypes, Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class LargeWindSpirit(SwirlChangeSummonBase):
    name: Literal['Large Wind Spirit'] = 'Large Wind Spirit'
    desc: str = (
        'End Phase: Deal 2 Anemo DMG. '
        'After your character or Summon triggers a Swirl reaction: Convert '
        'the Elemental Type of this card and change its DMG dealt to the '
        'element Swirled. (Can only be converted once before leaving the '
        'field)'
    )
    talent_desc: str = (
        '. When this card has converted to another Elemental Type: Deal +1 '
        'DMG of this Elemental Type.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3
    damage: int = 2
    talent_activated: bool = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = self.desc.replace(self.talent_desc, '')
            self.desc += self.talent_desc

    def renew(self, obj: 'LargeWindSpirit') -> None:
        super().renew(obj)
        if obj.talent_activated and not self.talent_activated:
            self.desc += self.talent_desc
            self.talent_activated = obj.talent_activated

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If talent activated, and damage type is not anemo, increase damage
        """
        if (
            not self.talent_activated 
            or self.damage_elemental_type == DamageElementalType.ANEMO
        ):
            # no talent or current is anemo
            return value
        if (
            value.position.player_idx != self.position.player_idx
            or value.target_position.player_idx == self.position.player_idx
        ):
            # enemy or attack self
            return value
        if value.damage_elemental_type != self.damage_elemental_type:
            # elemental type not match
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


# Skills


class AstableAnemohypostasisCreation6308(ElementalSkillBase):
    name: Literal[
        'Astable Anemohypostasis Creation - 6308'
    ] = 'Astable Anemohypostasis Creation - 6308'
    desc: str = (
        'Deals 3 Anemo DMG, the target is forcibly switched to the previous '
        'character.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        prev_idx = match.player_tables[
            1 - self.position.player_idx].previous_charactor_idx()
        if prev_idx is None:
            return ret
        # change charactor
        attack_action = ret[0]
        assert attack_action.type == ActionTypes.MAKE_DAMAGE
        attack_action.do_charactor_change = True
        attack_action.charactor_change_idx = prev_idx
        return ret


class ForbiddenCreationIsomer75TypeII(ElementalBurstBase):
    name: Literal[
        'Forbidden Creation - Isomer 75 / Type II'
    ] = 'Forbidden Creation - Isomer 75 / Type II'
    desc: str = 'Deals 1 Anemo DMG, summons 1 Large Wind Spirit.'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        args = { 'talent_activated': self.is_talent_equipped(match) }
        return [
            self.create_summon('Large Wind Spirit', args)
        ] + super().get_actions(match)


# Talents


class ChaoticEntropy(SkillTalent):
    name: Literal['Chaotic Entropy']
    desc: str = (
        'Combat Action: When your active character is Sucrose, equip this '
        'card. After Sucrose equips this card, immediately use Forbidden '
        'Creation - Isomer 75 / Type II once. After the Large Wind Spirit '
        'created by your Sucrose, who had this card equipped, has converted '
        'to another Elemental Type: Deal +1 DMG of this Elemental Type.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Sucrose'] = 'Sucrose'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: ForbiddenCreationIsomer75TypeII = ForbiddenCreationIsomer75TypeII()


# charactor base


class Sucrose(CharactorBase):
    name: Literal['Sucrose']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Harmless Sweetie" Sucrose'''
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | AstableAnemohypostasisCreation6308 
        | ForbiddenCreationIsomer75TypeII
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: ChaoticEntropy | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Wind Spirit Creation',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            AstableAnemohypostasisCreation6308(),
            ForbiddenCreationIsomer75TypeII()
        ]
