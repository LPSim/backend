from typing import Any, List, Literal

from ....modifiable_values import DamageIncreaseValue

from ....event import SkillEndEventArguments

from ....consts import ObjectPositionType, SkillType

from ....action import ChargeAction

from ....struct import Cost
from .base import ArtifactBase, RoundEffectArtifactBase


class OrnateKabuto(ArtifactBase):
    name: Literal['Ornate Kabuto'] = 'Ornate Kabuto'
    desc: str = (
        'After another character of yours uses an Elemental Burst: The '
        'character to which this is attached gains 1 Energy.'
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        if not (
            self.position.area == ObjectPositionType.CHARACTOR
            and event.action.position.player_idx == self.position.player_idx 
            and event.action.position.charactor_idx 
            != self.position.charactor_idx
            and event.action.skill_type == SkillType.ELEMENTAL_BURST
        ):
            # not equipped or not our other use burst
            return []
        # charge self by 1
        return [ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = self.position.charactor_idx,
            charge = 1
        )]


class EmblemOfSeveredFate(OrnateKabuto, RoundEffectArtifactBase):
    name: Literal['Emblem of Severed Fate'] = 'Emblem of Severed Fate'
    desc: str = (
        'After a character uses an Elemental Burst: The character to which '
        'this is attached gains 1 Energy. The DMG dealt by the '
        "character's Elemental Bursts is increased by 2. (Once per Round)"
    )
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_BURST
        ):
            # not self use elemental burst
            return value
        if self.usage <= 0:
            # no usage left
            return value
        # modify damage
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += 2
        return value


EmblemOfSeveredFateArtifacts = OrnateKabuto | EmblemOfSeveredFate
