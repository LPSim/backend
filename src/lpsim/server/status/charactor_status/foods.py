from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...consts import (
    CostLabels, DamageElementalType, IconType, ObjectPositionType, 
    SkillType
)

from ...modifiable_values import CostValue, DamageIncreaseValue

from ...action import RemoveObjectAction, SkillEndAction

from ...event import MakeDamageEventArguments
from .base import (
    DefendCharactorStatus, RoundCharactorStatus, RoundEndAttackCharactorStatus,
    UsageCharactorStatus
)


class Satiated_3_3(RoundCharactorStatus):
    name: Literal['Satiated'] = 'Satiated'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.FOOD] = IconType.FOOD


class JueyunGuoba_3_3(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal['Jueyun Guoba'] = 'Jueyun Guoba'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When this charactor use Elemental Burst, add 3 damage.

        Although it seems allow increase background damage, but as no
        skill will damage only background, it will be sonsumed when foreground
        charactor receives damage, and we do not need to check it.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use elemental burst, not modify
            return value
        if self.usage <= 0:
            # no usage, not modify
            return value
        # elemental burst, modify
        value.damage += 1
        self.usage -= 1
        return value


class AdeptusTemptation_3_3(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal["Adeptus' Temptation"] = "Adeptus' Temptation"
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When this charactor use Elemental Burst, add 3 damage.

        Although it seems allow increase background damage, but as no
        skill will damage only background, it will be sonsumed when foreground
        charactor receives damage, and we do not need to check it.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_BURST
        ):
            # not this charactor use elemental burst, not modify
            return value
        if self.usage <= 0:
            # no usage, not modify
            return value
        # elemental burst, modify
        value.damage += 3
        self.usage -= 1
        return value


class LotusFlowerCrisp_3_3(DefendCharactorStatus, RoundCharactorStatus):
    name: Literal['Lotus Flower Crisp'] = 'Lotus Flower Crisp'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 3


class NorthernSmokedChicken_3_3(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal['Northern Smoked Chicken']
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If this charactor use normal attack, decrease one unaligned die cost.
        """
        if self.usage <= 0:  # pragma: no cover
            # no usage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not charactor use skill, not modify
            return value
        if value.cost.label & CostLabels.NORMAL_ATTACK.value == 0:
            # not normal attack, not modify
            return value
        # modify
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value


class MushroomPizza_3_3(RoundEndAttackCharactorStatus):
    name: Literal['Mushroom Pizza'] = 'Mushroom Pizza'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.HEAL] = IconType.HEAL
    damage: int = -1
    damage_elemental_type: DamageElementalType = DamageElementalType.HEAL


class MintyMeatRolls_3_4(RoundCharactorStatus):
    name: Literal['Minty Meat Rolls'] = 'Minty Meat Rolls'
    version: Literal['3.4'] = '3.4'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    decrease_usage: int = 3

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If this charactor use normal attack, decrease one unaligned die cost.
        """
        if self.decrease_usage <= 0:  # pragma: no cover
            # no usage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not charactor use skill, not modify
            return value
        if value.cost.label & CostLabels.NORMAL_ATTACK.value == 0:
            # not normal attack, not modify
            return value
        # modify
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.decrease_usage -= 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndAction, match: Any
    ) -> List[RemoveObjectAction]:
        if self.decrease_usage == 0:
            self.usage = 0
        return self.check_should_remove()


class MintyMeatRolls_3_3(MintyMeatRolls_3_4):
    version: Literal['3.3']
    decrease_usage: int = 999


class SashiMiPlatter_3_7(RoundCharactorStatus):
    name: Literal['Sashimi Platter'] = 'Sashimi Platter'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When this charactor use Elemental Burst, add 3 damage.

        Although it seems allow increase background damage, but as no
        skill will damage only background, it will be sonsumed when foreground
        charactor receives damage, and we do not need to check it.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use elemental burst, not modify
            return value
        if value.damage_elemental_type == DamageElementalType.PIERCING:
            # piercing, not modify
            return value
        # elemental burst, modify
        value.damage += 1
        return value


class TandooriRoastChicken_3_7(RoundCharactorStatus):
    name: Literal['Tandoori Roast Chicken'] = 'Tandoori Roast Chicken'
    version: Literal['3.7'] = '3.7'
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When this charactor use Elemental Skill, add 2 damage.
        Logic same as AdeptusTemptation.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_SKILL
        ):
            # not this charactor use elemental skill, not modify
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, not modify
            return value
        # elemental burst, modify
        value.damage += 2
        self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


class ButterCrab_3_7(DefendCharactorStatus, RoundCharactorStatus):
    name: Literal['Butter Crab'] = 'Butter Crab'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 2


register_class(
    Satiated_3_3 | JueyunGuoba_3_3 | AdeptusTemptation_3_3 
    | LotusFlowerCrisp_3_3 | NorthernSmokedChicken_3_3 | MushroomPizza_3_3 
    | MintyMeatRolls_3_3 | MintyMeatRolls_3_4 
    | SashiMiPlatter_3_7 | TandooriRoastChicken_3_7 | ButterCrab_3_7
)
