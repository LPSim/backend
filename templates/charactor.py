# type: ignore


from typing import Any, List, Literal

from ...utils.class_registry import register_class

from ...utils.desc_registry import DescDictType

from ...summon.base import ShieldSummonBase, AttackerSummonBase

from ...modifiable_values import CombatActionValue, DamageIncreaseValue
from ...event import RoundPrepareEventArguments

from ...action import Actions, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Charactor status.


# Round status, will last for several rounds and disappear
class ...(RoundCharactorStatus):
    name: Literal[...] = ...
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
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    min_damage_to_trigger: int = ...
    max_in_one_time: int = ...


# Shieldstatus, i.e. yellow shield.
class ...(ShieldCharactorStatus):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...


# Team status. 


# Refer to above, change XXXCharactorStatus to XXXTeamStatus.
...


# Summons


class ...(AttackerSummonBase):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = ...


class ...(DefendSummonBase):
    name: Literal[...] = ...
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
    version: Literal[...] = ...
    charactor_name: Literal[...] = ...
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = ...
        charge = ...
    )
    skill: Literal[...] = ...

    def event_handler_...(
        self, event: ..., 
        match: Any
    ) -> List[Actions]:
        # triggers event handler


# charactor base


# charactor class name should contain its version.
class CNAME_X_X(CharactorBase):
    name: Literal["CNAME"]
    version: Literal['VERSION'] = 'VERSION'
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

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = ...,
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
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


# define descriptions of newly defined classes. Note key of skills and talents
# have charactor names. For balance changes, only descs are needed to define.
charactor_descs: Dict[str, DescDictType] = {
    # charactor information. descs are optional but must define version number.
    # id is used to sort in the frontend.
    "CHARACTOR/CNAME_X_X": {
        "image_path": "charactor/...",
        "id": ...,
        "names": {
            "zh-CN": "...",
            "en-US": "CNAME_X_X"
        },
        "descs": {
            "VERSION": {
                "zh-CN": "",
                "en-US": ""
            }
        }
    },
    # charactor skills, with SKILL_${cname}_${skill_type} as key.
    "SKILL_CNAME_X_X_NORMAL_ATTACK/...": {
        "names": {
            "zh-CN": "XXX",
            "en-US": "XXX"
        },
        "descs": {
            "VERSION": {
                "zh-CN": "",
                "en-US": ""
            }
        }
    },
    ...,
    # charactor talents, with TALENT_${cname}_${talent_name} as key.
    "TALENT_CNAME_X_X/...": {
        "image_path": "charactor/...",
        "id": ...,
        "names": {
            "zh-CN": "XXX",
            "en-US": "XXX"
        },
        "descs": {
            "VERSION": {
                "zh-CN": "",
                "en-US": ""
            }
        }
    },
    # summons
    "SUMMON/...": {
        "image_path": "summon/...",
        "names": {
            "zh-CN": "XXX",
            "en-US": "XXX"
        },
        "descs": {
            "VERSION": {
                "zh-CN": "",
                "en-US": ""
            }
        }
    },
    # status
    "CHARACTOR_STATUS/...": {
        "image_path": "status/...",
        "names": {
            "zh-CN": "XXX",
            "en-US": "XXX"
        },
        "descs": {
            "VERSION": {
                # you can use reference key to reference other desc
                "zh-CN": "$CHARACTOR_STATUS/...|descs|OLD_VERSION",
                "en-US": ""
            }
        }
    },
}


register_class(
    CNAME_X_X | Talent | Summon | Status,
    charactor_descs
)
