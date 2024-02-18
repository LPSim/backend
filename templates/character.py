# type: ignore


from typing import List, Literal

from lpsim.utils.class_registry import register_class

from lpsim.utils.desc_registry import DescDictType
from lpsim.server.summon.base import ShieldSummonBase, AttackerSummonBase
from lpsim.server.modifiable_values import CombatActionValue, DamageIncreaseValue
from lpsim.server.event import RoundPrepareEventArguments
from lpsim.server.action import Actions, CreateObjectAction
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, ObjectPositionType, WeaponType
)
from lpsim.server.character.character_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharacterBase, SkillTalent
)


# Character status.


# Round status, will last for several rounds and disappear
class ...(RoundCharacterStatus):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...

    def event_handler_...(
        self, event: ..., 
        match: Match
    ) -> List[Actions]:
        ...


# Usage status, will not disappear until usage is 0
class ...(UsageCharacterStatus):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...

    def event_handler_...(
        self, event: ..., 
        match: Match
    ) -> List[Actions]:
        ...


# Defend status, i.e. purple shield. They inherit UsageCharacterStatus
class ...(DefendCharacterStatus):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...
    min_damage_to_trigger: int = ...
    max_in_one_time: int = ...


# Shieldstatus, i.e. yellow shield.
class ...(ShieldCharacterStatus):
    name: Literal[...] = ...
    version: Literal[...] = ...
    usage: int = ...
    max_usage: int = ...


# Team status. 


# Refer to above, change XXXCharacterStatus to XXXTeamStatus.
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

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [self.create_summon('...'),
            self.create_character_status('...'),
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

    def get_actions(self, match: Match) -> List[Actions]:
        ...


class ...(PassiveSkillBase):
    name: Literal[...] = ...
    usage: int = ...

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        When in round prepare, reset usage
        """
        self.usage = ...
        return []

    def value_modifier_...(
        self, value: ..., 
        match: Match,
        mode: Literal['TEST', 'REAL'],
    ) -> ...:
        # triggers value modifier
        ...


# Talents


class ...(SkillTalent):
    name: Literal[...]  # Do not set default value for talent card
    version: Literal[...] = ...
    character_name: Literal[...] = ...
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = ...
        charge = ...
    )
    skill: Literal[...] = ...

    def event_handler_...(
        self, event: ..., 
        match: Match
    ) -> List[Actions]:
        # triggers event handler


# character base


# character class name should contain its version.
class CNAME_X_X(CharacterBase):
    name: Literal['CNAME']
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
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    # character information. descs are optional but must define version number.
    # id is used to sort in the frontend.
    "CHARACTER/CNAME_X_X": {
        "image_path": "character/...",
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
    # character skills, with SKILL_${cname}_${skill_type} as key.
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
    # character talents, with TALENT_${cname}_${talent_name} as key.
    "TALENT_CNAME_X_X/...": {
        "image_path": "character/...",
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
    "CHARACTER_STATUS/...": {
        "image_path": "status/...",
        "names": {
            "zh-CN": "XXX",
            "en-US": "XXX"
        },
        "descs": {
            "VERSION": {
                # you can use reference key to reference other desc
                "zh-CN": "$CHARACTER_STATUS/...|descs|OLD_VERSION",
                "en-US": ""
            }
        }
    },
}


register_class(
    CNAME_X_X | Talent | Summon | Status,
    character_descs
)
