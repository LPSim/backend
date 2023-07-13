"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. Base class of complex objects (e.g. cards and charactors) should 
be defined in their own files.
"""


from utils import BaseModel
from typing import List, Literal
from .action import ActionTypes
from .consts import (
    ObjectType, WeaponType, ElementType, DamageType, SkillType,
    ELEMENT_TO_DIE_COLOR,
)
from .modifiable_values import DiceCostValue


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    player_id: int = -1
    index: int = 0
    _object_id: int = -1
    event_triggers: List[ActionTypes] = []


class SkillBase(ObjectBase):
    """
    Base class of skills.
    """
    name: str
    type: Literal[ObjectType.SKILL] = ObjectType.SKILL
    damage: int
    cost: DiceCostValue


class PhysicalNormalAttackBase(SkillBase):
    """
    Base class of physical normal attacks.
    """
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageType = DamageType.PHYSICAL
    damage: int = 2

    @staticmethod
    def get_cost(element: ElementType) -> DiceCostValue:
        return DiceCostValue(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalNormalAttackBase(SkillBase):
    """
    Base class of elemental normal attacks.
    """
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageType
    damage: int = 1

    @staticmethod
    def get_cost(element: ElementType) -> DiceCostValue:
        return DiceCostValue(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalSkillBase(SkillBase):
    """
    Base class of elemental skills.
    """
    skill_type: Literal[SkillType.ELEMENTAL_SKILL] = SkillType.ELEMENTAL_SKILL
    damage_type: DamageType
    damage: int = 3

    @staticmethod
    def get_cost(element: ElementType) -> DiceCostValue:
        return DiceCostValue(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 3,
        )


class ElementalBurstBase(SkillBase):
    """
    Base class of elemental bursts.
    """
    skill_type: Literal[SkillType.ELEMENTAL_BURST] = SkillType.ELEMENTAL_BURST
    damage_type: DamageType

    @staticmethod
    def get_cost(element: ElementType, number: int) -> DiceCostValue:
        return DiceCostValue(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = number,
        )


class WeaponBase(ObjectBase):
    """
    Base class of weapons.
    """
    name: str
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    weapon_type: WeaponType


class ArtifactBase(ObjectBase):
    """
    Base class of artifacts.
    """
    name: str
    type: Literal[ObjectType.ARTIFACT] = ObjectType.ARTIFACT


class TalentBase(ObjectBase):
    """
    Base class of talents.
    """
    name: str
    type: Literal[ObjectType.TALENT] = ObjectType.TALENT


class StatusBase(ObjectBase):
    """
    Base class of status.
    """
    name: str
    type: Literal[ObjectType.CHARACTOR_STATUS, ObjectType.TEAM_STATUS]


class CharactorStatusBase(StatusBase):
    """
    Base class of charactor status.
    """
    type: Literal[ObjectType.CHARACTOR_STATUS] = ObjectType.CHARACTOR_STATUS


class TeamStatusBase(StatusBase):
    """
    Base class of team status.
    """
    type: Literal[ObjectType.TEAM_STATUS] = ObjectType.TEAM_STATUS
