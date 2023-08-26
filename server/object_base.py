"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. Base class of complex objects (e.g. cards and charactors) should 
be defined in their own files.
"""


import time
import random
from utils import BaseModel
from typing import List, Literal, Any
from .action import (
    ActionBase, ActionTypes, Actions, MakeDamageAction, ChargeAction
)
from .consts import (
    ObjectType, WeaponType, ElementType, DamageElementalType, SkillType,
    DamageType, DamageSourceType, ELEMENT_TO_DIE_COLOR, ObjectPositionType,
    DiceCostLabels,
)
from .modifiable_values import ModifiableValueTypes, DamageValue
from .struct import (
    ObjectPosition, DiceCost, CardActionTarget
)
from .interaction import RequestActionType


used_object_ids = set()


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    position: ObjectPosition
    id: int = 0

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
        # if id is zero, generate a new id
        if self.id == 0:
            while True:
                self.id = (
                    int(time.time() % 86400 * 1000000) 
                    * 1024 + random.randint(0, 1023)
                )
                if self.id not in used_object_ids:
                    break
        used_object_ids.add(self.id)


class SkillBase(ObjectBase):
    """
    Base class of skills.
    """
    name: str
    desc: str
    type: Literal[ObjectType.SKILL] = ObjectType.SKILL
    damage_type: DamageElementalType
    damage: int
    cost: DiceCost
    cost_label: int
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        charactor_id = -1,
        area = ObjectPositionType.INVALID
    )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set id to 0, as skills are not real objects
        self.id = 0
        # set cost label into cost
        self.cost.label = self.cost_label
        if self.cost.original_value is not None:
            self.cost.original_value.label = self.cost_label

    def is_valid(self, match: Any) -> bool:
        """
        Check if the skill can be used.
        """
        return True

    def get_actions(self, match: Any) -> List[Actions]:
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
                player_id = self.position.player_id,
                charactor_id = self.position.charactor_id,
                charge = 1,
            ),
            MakeDamageAction(
                player_id = self.position.player_id,
                target_id = 1 - self.position.player_id,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        id = self.id,
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
    desc: str = """Deals 2 Physical DMG."""
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    damage: int = 2
    cost_label: int = DiceCostLabels.NORMAL_ATTACK.value

    @staticmethod
    def get_cost(element: ElementType) -> DiceCost:
        return DiceCost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalNormalAttackBase(SkillBase):
    """
    Base class of elemental normal attacks.
    """
    desc: str = """Deals 1 _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType
    damage: int = 1
    cost_label: int = DiceCostLabels.NORMAL_ATTACK.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> DiceCost:
        return DiceCost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalSkillBase(SkillBase):
    """
    Base class of elemental skills.
    """
    desc: str = """Deals 3 _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.ELEMENTAL_SKILL] = SkillType.ELEMENTAL_SKILL
    damage_type: DamageElementalType
    damage: int = 3
    cost_label: int = DiceCostLabels.ELEMENTAL_SKILL.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> DiceCost:
        return DiceCost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 3,
        )


class ElementalBurstBase(SkillBase):
    """
    Base class of elemental bursts.
    """
    desc: str = """Deals _DAMAGE_ _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.ELEMENTAL_BURST] = SkillType.ELEMENTAL_BURST
    damage_type: DamageElementalType
    charge: int
    cost_label: int = DiceCostLabels.ELEMENTAL_BURST.value

    @staticmethod
    def get_cost(element: ElementType, number: int) -> DiceCost:
        return DiceCost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = number,
        )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())
        self.desc = self.desc.replace('_DAMAGE_', str(self.damage))

    def is_valid(self, match: Any) -> bool:
        """
        Check if the skill can be used.
        """
        table = match.player_tables[self.position.player_id]
        charactor = table.charactors[self.position.charactor_id]
        return self.charge <= charactor.charge

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When using elemental burst, the charge of the active charactor will be
        reduced by `self.charge`.
        """
        actions = super().get_actions(match)
        for action in actions:
            if isinstance(action, ChargeAction):
                action.charge = -self.charge
        return actions


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: str
    desc: str
    type: Literal[ObjectType.CARD, ObjectType.WEAPON, ObjectType.ARTIFACT,
                  ObjectType.TALENT, ObjectType.SUMMON,
                  ObjectType.SUPPORT] = ObjectType.CARD
    version: str
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        charactor_id = -1,
        area = ObjectPositionType.INVALID
    )
    cost: DiceCost
    cost_label: int = DiceCostLabels.CARD.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set cost label into cost
        self.cost.label = self.cost_label
        if self.cost.original_value is not None:
            self.cost.original_value.label = self.cost_label

    @property
    def action_type(self) -> RequestActionType:
        """
        Return the action type of the card.
        """
        return RequestActionType.QUICK

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        """
        Get the targets of the card.
        """
        raise NotImplementedError

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[ActionBase]:
        """
        Act the card. It will return a list of actions.

        Arguments:
            args (CardActionArguments | None): The arguments of the action.
                for cards that do not need to specify target, args is None.
            match (Any): The match object.
        """
        raise NotImplementedError()

    def is_valid(self, match: Any) -> bool:
        """
        Check if the card can be used. Note that this function will not check
        the cost of the card.
        """
        return True


class WeaponBase(CardBase):
    """
    Base class of weapons.
    """
    name: str
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    cost_label: int = DiceCostLabels.CARD.value | DiceCostLabels.WEAPON.value
    weapon_type: WeaponType
