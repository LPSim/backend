"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. Base class of complex objects (e.g. cards and charactors) should 
be defined in their own files.
"""


from utils import BaseModel
from typing import List, Literal
from .action import (
    ActionBase, ActionTypes, Actions, MakeDamageAction, ChargeAction
)
from .consts import (
    ObjectType, WeaponType, ElementType, DamageElementalType, SkillType,
    DamageType, DamageSourceType, ELEMENT_TO_DIE_COLOR, ObjectPositionType,
)
from .modifiable_values import ModifiableValueTypes, DiceCostValue, DamageValue
from .struct import SkillActionArguments, ObjectPosition


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    index: int = 0
    position: ObjectPosition

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # check event handler name valid
        for k in dir(self):
            if k[:14] == 'event_handler_':
                k = k[14:]
                try:
                    k = ActionTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid event handler name: {k}')
            if k[:15] == 'value_modifier_':
                k = k[15:]
                try:
                    k = ModifiableValueTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid value modifier name: {k}')


class SkillBase(ObjectBase):
    """
    Base class of skills.
    """
    name: str
    type: Literal[ObjectType.SKILL] = ObjectType.SKILL
    damage_type: DamageElementalType
    damage: int
    cost: DiceCostValue
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        charactor_id = -1,
        area = ObjectPositionType.INVALID
    )

    def is_valid(self, hp: int, charge: int) -> bool:
        """
        Check if the skill can be used.
        """
        return True

    def get_actions(self, args: SkillActionArguments) -> List[Actions]:
        """
        The skill is triggered, and get actions of the skill.
        By default, it will generate three actions:
        1. MakeDamageAction to attack the enemy active charactor with damage
            `self.damage` and damage type `self.damage_type`.
        2. ChargeAction to charge the active charactor by 1.
        3. SkillEndAction to declare skill end, and trigger the event.
        """
        return [
            ChargeAction(
                player_id = args.player_id,
                charactor_id = args.our_active_charactor_id,
                charge = 1,
            ),
            MakeDamageAction(
                player_id = args.player_id,
                target_id = 1 - args.player_id,
                damage_value_list = [
                    DamageValue(
                        player_id = args.player_id,
                        damage_type = DamageType.DAMAGE,
                        damage_source_type
                        = DamageSourceType.CURRENT_PLAYER_CHARACTOR,
                        damage = self.damage,
                        damage_elemental_type = self.damage_type,
                        charge_cost = 0,
                        target_player = 'ENEMY',
                        target_charactor = 'ACTIVE',
                    )
                ],
                charactor_change_rule = 'NONE'
            ),
        ]


class PhysicalNormalAttackBase(SkillBase):
    """
    Base class of physical normal attacks.
    """
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
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
    damage_type: DamageElementalType
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
    damage_type: DamageElementalType
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
    damage_type: DamageElementalType
    charge: int

    @staticmethod
    def get_cost(element: ElementType, number: int) -> DiceCostValue:
        return DiceCostValue(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = number,
        )

    def is_valid(self, hp: int, charge: int) -> bool:
        """
        Check if the skill can be used.
        """
        return self.charge <= charge

    def get_actions(self, args: SkillActionArguments) -> List[Actions]:
        """
        When using elemental burst, the charge of the active charactor will be
        reduced by `self.charge`.
        """
        actions = super().get_actions(args)
        for action in actions:
            if isinstance(action, ChargeAction):
                action.charge = -self.charge
        return actions


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: str
    type: Literal[ObjectType.CARD, ObjectType.WEAPON, ObjectType.ARTIFACT,
                  ObjectType.TALENT, ObjectType.SUMMON,
                  ObjectType.SUPPORT] = ObjectType.CARD
    version: str
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        charactor_id = -1,
        area = ObjectPositionType.INVALID
    )

    def get_actions(self) -> List[ActionBase]:
        """
        Act the card. It will return a list of actions.
        """
        raise NotImplementedError()


class WeaponBase(CardBase):
    """
    Base class of weapons.
    """
    name: str
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    weapon_type: WeaponType


class ArtifactBase(CardBase):
    """
    Base class of artifacts.
    """
    name: str
    type: Literal[ObjectType.ARTIFACT] = ObjectType.ARTIFACT


class TalentBase(CardBase):
    """
    Base class of talents.
    """
    name: str
    type: Literal[ObjectType.TALENT] = ObjectType.TALENT
