# type: ignore


from typing import Any, List, Literal

from ...summon.base import ShieldSummonBase, AttackerSummonBase

from ...modifiable_values import CombatActionValue, DamageIncreaseValue
from ...event import RoundPrepareEventArguments

from ...action import Actions, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear
class ...(RoundCharactorStatus):
    name: Literal[...] = ...
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...

    def event_handler_...(
        self, event: ..., 
        match: Any
    ) -> List[Actions]:
        ...


# Usage status, will not disappear until usage is 0
class ...(UsageCharactorStatus):
    name: Literal[...] = ...
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...

    def event_handler_...(
        self, event: ..., 
        match: Any
    ) -> List[Actions]:
        ...


# Defend status, i.e. purple shield. They inherit UsageCharactorStatus
class ...(DefendCharactorStatus):
    name: Literal[...] = ...
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    min_damage_to_trigger: int = ...
    max_in_one_time: int = ...


# Shieldstatus, i.e. yellow shield.
class ...(ShieldCharactorStatus):
    name: Literal[...] = ...
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...


# Team status. DO NOT define here, define in server/status/team_status
# Here is just example.


# Refer to above, change XXXCharactorStatus to XXXTeamStatus.
...


# Summons


class ...(AttackerSummonBase):
    name: Literal[...]
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = ...


class ...(DefendSummonBase):
    name: Literal[...] = ...
    desc: str = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = ...
    min_damage_to_trigger: int = ...
    max_in_one_time: int = ...
    attack_until_run_out_of_usage: bool = ...


# Skills


class ...(ElementalSkillBase):
    name: Literal[...] = ...
    desc: str = ...
    damage: int = ...
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('...'),
            self.create_charactor_status('...'),
            self.create_team_status('...'),
        ]


class ...(ElementalBurstBase):
    name: Literal[...] = ...
    desc: str = ...
    damage: int = ...
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = ...
        charge = ...
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ...


class ...(PassiveSkillBase):
    name: Literal[...] = ...
    desc: str = ...
    usage: int = ...

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, reset usage
        """
        self.usage = ...
        return []

    def value_modifier_...(
        self, value: ..., 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> ...:
        # triggers value modifier
        ...


# Talents


class ...(SkillTalent):
    name: Literal[...]  # Do not set default value for talent card
    desc: str = ...
    version: Literal[...] = ...
    charactor_name: Literal[...] = ...
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = ...
        charge = ...
    )
    skill: ... = ...()

    def event_handler_...(
        self, event: ..., 
        match: Any
    ) -> List[Actions]:
        # triggers event handler


# charactor base


class ...(CharactorBase):
    name: Literal[...]  # Do not set default value for charactor name
    version: Literal[...] = ...
    desc: str = ...
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = ...
    skills: List[
        ElementalNormalAttackBase | PhysicalNormalAttackBase
        | ...(ElementalSkillBase) | ...(ElementalBurstBase)
    ] = []
    faction: List[FactionType] = [
        FactionType.
    ]
    weapon_type: WeaponType = WeaponType.
    talent: ... | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = ...,
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            PhysicalNormalAttackBase(
                name = ...,
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ...(),
            ...(),
            ...(),
        ]


# finally, modify server/charactor/(element)/__init__.py
