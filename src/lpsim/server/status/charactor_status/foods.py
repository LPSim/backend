from typing import Any, List, Literal

from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DamageType, IconType, ObjectPositionType, 
    SkillType
)

from ...modifiable_values import CostValue, DamageIncreaseValue, DamageValue

from ...action import MakeDamageAction, RemoveObjectAction, SkillEndAction

from ...event import MakeDamageEventArguments, RoundEndEventArguments
from .base import (
    DefendCharactorStatus, RoundCharactorStatus, UsageCharactorStatus
)


class Satiated(RoundCharactorStatus):
    name: Literal['Satiated'] = 'Satiated'
    desc: str = 'You cannot consume more Food this Round'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.FOOD] = IconType.FOOD


class JueyunGuoba(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal['Jueyun Guoba'] = 'Jueyun Guoba'
    desc: str = (
        "During this Round, the target character's next Normal Attack "
        "deals +1 DMG."
    )
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


class AdeptusTemptation(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal["Adeptus' Temptation"] = "Adeptus' Temptation"
    desc: str = (
        "During this Round, the target character's next Elemental Burst "
        "deals +3 DMG."
    )
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


class LotusFlowerCrisp(DefendCharactorStatus, RoundCharactorStatus):
    name: Literal['Lotus Flower Crisp'] = 'Lotus Flower Crisp'
    desc: str = (
        "During this Round, the target character takes -3 DMG the next time."
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 3


class NorthernSmokedChicken(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal['Northern Smoked Chicken']
    desc: str = (
        "During this Round, the target character's next Normal Attack cost "
        "less 1 Unaligned Element."
    )
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


class MushroomPizza(RoundCharactorStatus):
    name: Literal['Mushroom Pizza'] = 'Mushroom Pizza'
    desc: str = (
        'End Phase: Heal this charactor for 1 HP. '
        'Usage(s): 2'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.HEAL] = IconType.HEAL

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        target_charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = target_charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        )]


class MintyMeatRolls(RoundCharactorStatus):
    name: Literal['Minty Meat Rolls'] = 'Minty Meat Rolls'
    desc: str = (
        "During this Round, the target character's next 3 Normal Attacks cost "
        "less 1 Unaligned Element."
    )
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


class SashiMiPlatter(RoundCharactorStatus):
    name: Literal['Sashimi Platter'] = 'Sashimi Platter'
    desc: str = (
        "During this Round, the target character's Normal Attacks "
        "deals +1 DMG."
    )
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
        if value.damage_from_element_reaction:
            # element reaction, not modify
            return value
        if value.damage_elemental_type == DamageElementalType.PIERCING:
            # piercing, not modify
            return value
        # elemental burst, modify
        value.damage += 1
        return value


class TandooriRoastChicken(RoundCharactorStatus):
    name: Literal['Tandoori Roast Chicken'] = 'Tandoori Roast Chicken'
    desc: str = (
        "During this Round, all your characters' next Elemental Skills "
        "deal +2 DMG."
    )
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
        if self.usage <= 0:
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


class ButterCrab(DefendCharactorStatus, RoundCharactorStatus):
    name: Literal['Butter Crab'] = 'Butter Crab'
    desc: str = (
        "During this Round, the target character takes -2 DMG the next time."
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 2


FoodStatus = (
    Satiated | JueyunGuoba | AdeptusTemptation | LotusFlowerCrisp 
    | NorthernSmokedChicken | MushroomPizza | MintyMeatRolls | SashiMiPlatter
    | TandooriRoastChicken | ButterCrab
)
