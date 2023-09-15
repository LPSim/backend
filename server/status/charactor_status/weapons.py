from typing import Any, List, Literal

from ...action import RemoveObjectAction

from ...event import MoveObjectEventArguments, UseSkillEventArguments

from ...consts import CostLabels, ObjectPositionType

from ...modifiable_values import CostValue
from .base import RoundCharactorStatus, ShieldCharactorStatus


class LithicSpear(ShieldCharactorStatus):
    name: Literal['Lithic Spear'] = 'Lithic Spear'
    desc: str = (
        'Grants XXX Shield point to defend your active charactor. '
    )
    version: Literal['3.3'] = '3.3'
    usage: int
    max_usage: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.desc = self.desc.replace('XXX', str(self.usage))

    def renew(self, object: 'LithicSpear') -> None:
        self.max_usage = object.max_usage
        self.usage = max(object.usage, self.usage)
        self.usage = min(self.max_usage, self.usage)
        self.desc = object.desc


class KingsSquire(RoundCharactorStatus):
    name: Literal["King's Squire"] = "King's Squire"
    desc: str = (
        'The character to which this '
        'is attached will spend 2 less Elemental Dice next time they use an '
        'Elemental Skill or equip a Talent card.'
    )
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If self use elemental skill, or equip talent, cost -2.
        """
        label = value.cost.label
        if label & (
            CostLabels.ELEMENTAL_SKILL.value | CostLabels.TALENT.value
        ) == 0:  # no label match
            return value
        position = value.position
        if position.player_idx != self.position.player_idx:
            # not same player
            return value
        assert self.position.charactor_idx != -1
        if position.area == ObjectPositionType.SKILL:
            # cost from charactor
            if position.charactor_idx != self.position.charactor_idx:
                # not same charactor
                return value
        else:
            # cost from hand card, is a talent card
            charactor = match.player_tables[
                self.position.player_idx
            ].charactors[self.position.charactor_idx]
            for card in match.player_tables[
                    self.position.player_idx].hands:
                if card.id == value.position.id:
                    if card.charactor_name != charactor.name:
                        # talent card not for this charactor
                        return value
        # decrease cost
        assert self.usage > 0
        decrease_result = [
            value.cost.decrease_cost(value.cost.elemental_dice_color),
            value.cost.decrease_cost(value.cost.elemental_dice_color),
        ]
        if True in decrease_result:  # pragma: no branch
            # decrease cost success
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


WeaponCharactorStatus = LithicSpear | KingsSquire
