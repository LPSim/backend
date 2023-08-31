from typing import Any, List, Literal

from ...consts import ObjectPositionType, SkillType

from ...modifiable_values import DamageIncreaseValue

from ...action import RemoveObjectAction

from ...event import MakeDamageEventArguments
from .base import RoundCharactorStatus


class Satiated(RoundCharactorStatus):
    name: Literal['Satiated'] = 'Satiated'
    desc: str = 'You cannot consume more Food this Round'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1


class AdeptusTemptation(RoundCharactorStatus):
    name: Literal["Adeptus' Temptation"]
    desc: str = (
        "During this Round, the target character's next Elemental Burst "
        "deals +3 DMG."
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

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
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True,
            target_area = ObjectPositionType.SKILL,
        ):
            # not this charactor use skill, not modify
            return value
        skill = match.get_object(value.position)
        skill_type: SkillType = skill.skill_type
        if skill_type != SkillType.ELEMENTAL_BURST:
            # not elemental burst, not modify
            return value
        if self.usage <= 0:
            # no usage, not modify
            return value
        # elemental burst, modify
        value.damage += 3
        self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


FoodStatus = Satiated | AdeptusTemptation
