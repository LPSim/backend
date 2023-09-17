
from typing import Any, List, Literal

from ...event import SkillEndEventArguments

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, CostLabels, DamageType, ElementType, 
    ObjectPositionType, SkillType
)

from ...action import CreateObjectAction, RemoveObjectAction

from ...modifiable_values import CostValue, DamageIncreaseValue

from .base import RoundTeamStatus, UsageTeamStatus


class Stormzone(UsageTeamStatus):
    name: Literal['Stormzone'] = 'Stormzone'
    desc: str = (
        'When you perform "Switch Character": Spend 1 less Elemental Die. '
        'Usage(s): 2'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2

    talent_activated: bool = False
    decrease_cost_success: bool = False
    updated_desc: str = (
        'When you perform "Switch Character": Spend 1 less Elemental Die. '
        'After this effect is triggered, your next Normal Attack this '
        'round will cost 1 less Unaligned Element. Usage(s): 2'
    )

    def renew(self, new_status: 'Stormzone') -> None:
        super().renew(new_status)
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = self.updated_desc

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)
        if self.talent_activated:
            # change desc
            self.desc = self.updated_desc

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        Decrease sw_char cost. 
        """
        if value.position.player_idx != self.position.player_idx:
            # not this player, do nothing
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR.value == 0:
            # not sw_char, do nothing
            return value
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.decrease_cost_success = True
                self.usage -= 1
        return value

    def event_handler_SWITCH_CHARACTOR(
        self, event: ..., 
        match: Any
    ) -> List[CreateObjectAction | RemoveObjectAction]:
        """
        if this status is talent activated, them create Winds of Harmony.
        Check if need to remove self.
        """
        if not self.decrease_cost_success:
            # not decrease cost success, do nothing
            return []
        self.decrease_cost_success = False
        ret: List[CreateObjectAction | RemoveObjectAction] = []
        if self.talent_activated:
            # create Winds of Harmony
            ret.append(CreateObjectAction(
                object_name = 'Winds of Harmony',
                object_position = self.position,
                object_arguments = {}
            ))
        ret += self.check_should_remove()
        return ret


# Usage status, will not disappear until usage is 0
class WindsOfHarmony(RoundTeamStatus):
    name: Literal['Winds of Harmony'] = 'Winds of Harmony'
    desc: str = (
        "During this round, your charactor's next Normal Attack costs 1 less "
        "Unaligned Element."
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode = Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        Decrease normal attack cost.
        """
        if self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            target_area = ObjectPositionType.SKILL,
        ):
            # this charactor use skill, check if normal attack
            skill = match.get_object(value.position)
            skill_type: SkillType = skill.skill_type
            if skill_type == SkillType.NORMAL_ATTACK:
                # normal attack, decrease cost
                if value.cost.decrease_cost(None):
                    # decrease success
                    if mode == 'REAL':
                        self.usage -= 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


class PoeticsOfFuubutsu(UsageTeamStatus):
    name: Literal[
        'Poetics of Fuubutsu: Pyro',
        'Poetics of Fuubutsu: Hydro',
        'Poetics of Fuubutsu: Electro',
        'Poetics of Fuubutsu: Cryo',
    ]
    desc: str = (
        'your Characters and Summons will deal +1 DMG for _ELEMENT_ DMG.'
    )
    version: Literal['3.8'] = '3.8'
    usage: int = 2
    max_usage: int = 2
    element: ElementType = ElementType.NONE

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)
        element_name = self.name.split()[-1]
        element = ElementType[element_name.upper()]
        self.element = element
        self.desc = self.desc.replace('_ELEMENT_', element.name.capitalize())

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If our charactor skill or summon deal corresponding elemental DMG, 
        increase DMG.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, do nothing
            return value
        if value.position.player_idx != self.position.player_idx:
            # not this player, do nothing
            return value
        if value.damage_elemental_type != ELEMENT_TO_DAMAGE_TYPE[self.element]:
            # not corresponding elemental DMG, do nothing
            return value
        if value.position.area not in [
            ObjectPositionType.SKILL, ObjectPositionType.SUMMON
        ]:
            # not charactor or summon, do nothing
            return value
        if value.damage_from_element_reaction:
            # damage from elemental reaction, do nothing
            return value
        # increase DMG
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += 1
        return value


AnemoTeamStatus = Stormzone | WindsOfHarmony | PoeticsOfFuubutsu
