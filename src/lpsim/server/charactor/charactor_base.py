"""
Base class of charactors. Each charactor should have its own file, the file
contains the charactor class, talent class, talent card class, skill classes.
DO NOT implement status, summons, weapons, artifacts, etc. in this file, which
will break the import loop.
"""


from typing import List, Literal, Any, Tuple, get_origin, get_type_hints

from pydantic import validator

from ..event import MoveObjectEventArguments, UseSkillEventArguments
from ..consts import (
    ELEMENT_TO_DIE_COLOR, DamageElementalType, DamageType, ObjectType, 
    PlayerActionLabels, SkillType, WeaponType, ElementType, FactionType, 
    ObjectPositionType, CostLabels
)
from ..object_base import (
    ObjectBase, CardBase
)
from ..struct import Cost, DeckRestriction, ObjectPosition
from ..modifiable_values import DamageValue
from ..status import CharactorStatus
from ..card.equipment.artifact import Artifacts
from ..card.equipment.weapon import Weapons
from ..action import (
    ChargeAction, CreateObjectAction, MakeDamageAction, MoveObjectAction, 
    RemoveObjectAction, Actions, SkillEndAction, UseSkillAction
)


class SkillBase(ObjectBase):
    """
    Base class of skills.
    """
    name: str
    desc: str
    type: Literal[ObjectType.SKILL] = ObjectType.SKILL
    skill_type: SkillType
    damage_type: DamageElementalType
    damage: int
    cost: Cost
    cost_label: int
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set cost label into cost
        self.cost.label = self.cost_label
        # based on charactor id, calculate skill id.

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        """
        Get the action type of using the skill.

        Returns:
            Tuple[int, bool]: The first element is the action label, the second
                element is whether the action type is a combat action.
        """
        return PlayerActionLabels.SKILL.value, True

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
        """
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.charge_self(1),
        ]

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Any
    ):
        """
        When use skill event triggered, check if this skill is used.
        If so, return self.get_actions()
        """
        if event.action.skill_position == self.position:
            return self.get_actions(match)
        return []

    # commonly used function for skills

    def is_talent_equipped(self, match: Any):
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return charactor.talent is not None

    def create_team_status(
        self, name: str, args: Any = {}
    ) -> CreateObjectAction:
        position = ObjectPosition(
            player_idx = self.position.player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1
        )
        return CreateObjectAction(
            object_name = name,
            object_position = position,
            object_arguments = args
        )

    def create_charactor_status(
        self, name: str, args: Any = {}
    ) -> CreateObjectAction:
        return CreateObjectAction(
            object_name = name,
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = args
        )

    def create_summon(
        self, name: str, args: Any = {}
    ) -> CreateObjectAction:
        position = ObjectPosition(
            player_idx = self.position.player_idx,
            area = ObjectPositionType.SUMMON,
            id = -1
        )
        return CreateObjectAction(
            object_name = name,
            object_position = position,
            object_arguments = args
        )

    def charge_self(
        self, charge: int
    ) -> ChargeAction:
        return ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = self.position.charactor_idx,
            charge = charge,
        )

    def attack_opposite_active(
        self, match: Any, damage: int, damage_type: DamageElementalType,
    ) -> MakeDamageAction:
        assert damage > 0
        target_table = match.player_tables[1 - self.position.player_idx]
        target_charactor_idx = target_table.active_charactor_idx
        target_charactor = target_table.charactors[target_charactor_idx]
        return MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target_charactor.position,
                    damage = damage,
                    damage_elemental_type = damage_type,
                    cost = self.cost.copy(),
                )
            ],
        )

    def heal_self(self, match: Any, heal: int) -> MakeDamageAction:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = - heal,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        )

    def element_application_self(
        self, match: Any, element: DamageElementalType
    ) -> MakeDamageAction:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.ELEMENT_APPLICATION,
                    target_position = charactor.position,
                    damage = 0,
                    damage_elemental_type = element,
                    cost = self.cost.copy(),
                )
            ],
        )


class PhysicalNormalAttackBase(SkillBase):
    """
    Base class of physical normal attacks.
    """
    desc: str = """Deals 2 Physical DMG."""
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    damage: int = 2
    cost_label: int = CostLabels.NORMAL_ATTACK.value

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
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
    cost_label: int = CostLabels.NORMAL_ATTACK.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
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
    cost_label: int = CostLabels.ELEMENTAL_SKILL.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
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
    cost_label: int = CostLabels.ELEMENTAL_BURST.value

    @staticmethod
    def get_cost(element: ElementType, number: int, charge: int) -> Cost:
        return Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = number,
            charge = charge
        )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())
        self.desc = self.desc.replace('_DAMAGE_', str(self.damage))

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When using elemental burst, the charge of the active charactor will be
        reduced by `self.charge`.
        """
        return [
            self.charge_self(-self.cost.charge),
            self.attack_opposite_active(match, self.damage, self.damage_type),
        ]


class AOESkillBase(SkillBase):
    """
    Base class that deals AOE damage. Can inherit this class after previous
    classes to do AOE attack. It will attack active charactor damage+element, 
    back chractor back_damage_piercing.
    """
    desc: str = (
        'Deals _ACTIVE_ _ELEMENT_ DMG, deals _BACK_ Piercing DMG to all '
        'opposing characters on standby.'
    )
    back_damage: int

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())
        self.desc = self.desc.replace('_ACTIVE_', str(self.damage))
        self.desc = self.desc.replace('_BACK_', str(self.back_damage))

    def attack_opposite_active(
        self, match: Any, damage: int, damage_type: DamageElementalType,
    ) -> MakeDamageAction:
        """
        For AOE, modify attack opposite to also attack back charactors
        """
        target_table = match.player_tables[1 - self.position.player_idx]
        target_charactor_idx = target_table.active_charactor_idx
        target_charactor = target_table.charactors[target_charactor_idx]
        charactors = target_table.charactors
        damage_action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target_charactor.position,
                    damage = damage,
                    damage_elemental_type = damage_type,
                    cost = self.cost.copy(),
                )
            ],
        )
        for cid, charactor in enumerate(charactors):
            if cid == target_table.active_charactor_idx:
                continue
            if charactor.is_defeated:
                continue
            damage_action.damage_value_list.append(
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = charactor.position,
                    damage = self.back_damage,
                    damage_elemental_type = DamageElementalType.PIERCING,
                    cost = self.cost.copy(),
                )
            )
        return damage_action


class PassiveSkillBase(SkillBase):
    """
    Base class of passive skills.
    It has no cost and is always invalid (cannot be used).
    It has triggers to make effects.
    """
    skill_type: Literal[SkillType.PASSIVE] = SkillType.PASSIVE
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    damage: int = 0
    cost: Cost = Cost()
    cost_label: int = 0

    def is_valid(self, match: Any) -> bool:
        """
        Passive skills are always invalid.
        """
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Passive skills are always invalid, so it will return an empty list.
        """
        raise AssertionError('Try to get actions of a passive skill')
        return []


class TalentBase(CardBase):
    """
    Base class of talents. Note almost all talents are skills, and will receive
    cost decrease from other objects.
    """
    name: str
    charactor_name: str
    type: Literal[ObjectType.TALENT] = ObjectType.TALENT
    cost_label: int = CostLabels.CARD.value | CostLabels.TALENT.value
    remove_when_used: bool = False

    def get_deck_restriction(self) -> DeckRestriction:
        """
        For talent cards, should contain the corresponding charactor.
        """
        return DeckRestriction(
            type = 'CHARACTOR', 
            name = self.charactor_name, 
            number = 1
        )

    def is_valid(self, match: Any) -> bool:
        """
        Only corresponding charactor is active charactor can equip this card.
        """
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError('Talent is not in hand')
        table = match.player_tables[self.position.player_idx]
        return (table.charactors[table.active_charactor_idx].name
                == self.charactor_name)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        For most talent cards, can quip only on active charactor.
        """
        table = match.player_tables[self.position.player_idx]
        charactor = table.charactors[table.active_charactor_idx]
        return [charactor.position]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
        """
        Act the talent. will place it into talent area.
        When other talent is equipped, remove the old one.
        For subclasses, inherit this and add other actions (e.g. trigger
        correcponding skills)
        """
        assert target is not None
        ret: List[Actions] = []
        table = match.player_tables[target.player_idx]
        charactor = table.charactors[target.charactor_idx]
        # check if need to remove current talent
        if charactor.talent is not None:
            ret.append(RemoveObjectAction(
                object_position = charactor.talent.position,
            ))
        new_position = charactor.position.set_id(self.position.id)
        ret.append(MoveObjectAction(
            object_position = self.position,
            target_position = new_position
        ))
        return ret

    def equip(self, match: Any) -> List[Actions]:
        return []

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When this talent is moved from hand to charactor, it is considered
        as equipped, and will call `self.equip`.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.HAND
            and event.action.target_position.area 
            == ObjectPositionType.CHARACTOR
        ):
            # this talent equipped from hand to charactor
            return self.equip(match)
        return []


class SkillTalent(TalentBase):
    """
    Talents that trigger skills. They will get skill as input, which is
    saved as a private variable.
    """

    skill: SkillBase

    def is_valid(self, match: Any) -> bool:
        """
        Both TalentBase and SkillBase should be valid.
        """
        return super().is_valid(match) and self.skill.is_valid(match)

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        """
        For skill talent, the action label contains SKILL and is a combat 
        action.
        """
        return (
            PlayerActionLabels.CARD.value | PlayerActionLabels.SKILL.value,
            True
        )

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
        ret = super().get_actions(target, match)
        assert len(ret) > 0
        assert ret[-1].type == 'MOVE_OBJECT'
        target_position = ret[-1].target_position
        target_charactor = match.player_tables[
            target_position.player_idx
        ].charactors[target_position.charactor_idx]
        skills: List[SkillBase] = target_charactor.skills
        for s in skills:
            if s.name == self.skill.name:
                self.skill.position = s.position
                break
        else:
            raise AssertionError('Skill not found')
        ret.append(UseSkillAction(
            skill_position = self.skill.position
        ))
        # skill used, add SkillEndAction
        ret.append(SkillEndAction(
            position = self.skill.position,
            target_position = match.player_tables[
                1 - self.skill.position.player_idx
            ].get_active_charactor().position,
            skill_type = self.skill.skill_type,
        ))
        return ret


class CharactorBase(ObjectBase):
    """
    Base class of charactors.
    """
    name: str
    desc: str
    strict_version_validation: bool = False  # default accept higher versions
    version: str
    type: Literal[ObjectType.CHARACTOR] = ObjectType.CHARACTOR
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )

    element: ElementType
    max_hp: int
    max_charge: int
    skills: List[SkillBase]

    # labels
    faction: List[FactionType]
    weapon_type: WeaponType

    # charactor status
    hp: int = 0
    charge: int = 0
    weapon: Weapons | None = None
    artifact: Artifacts | None = None
    talent: TalentBase | None = None
    status: List[CharactorStatus] = []
    element_application: List[ElementType] = []
    is_alive: bool = True

    @validator('version', pre = True)
    def accept_same_or_higher_version(cls, v: str, values):  # pragma: no cover
        msg = 'version annotation must be Literal with one str'
        if not isinstance(v, str):
            raise NotImplementedError(msg)
        version_hints = get_type_hints(cls)['version']
        if get_origin(version_hints) != Literal:
            raise NotImplementedError(msg)
        version_hints = version_hints.__args__
        if len(version_hints) > 1:
            raise NotImplementedError(msg)
        version_hint = version_hints[0]
        if values['strict_version_validation'] and v != version_hint:
            raise ValueError(
                f'version {v} is not equal to {version_hint}'
            )
        if v < version_hint:
            raise ValueError(
                f'version {v} is lower than {version_hint}'
            )
        return version_hint

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.hp = self.max_hp
        old_skill_ids = [x.id for x in self.skills]
        self._init_skills()
        if len(old_skill_ids):
            new_skill_ids = [x.id for x in self.skills]
            if len(new_skill_ids) != len(old_skill_ids):
                raise AssertionError('Skill number changed after init')
            for id, skill in zip(old_skill_ids, self.skills):
                skill.id = id
                skill.position = skill.position.set_id(id)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        When position is edited, update skill positions.
        """
        super().__setattr__(name, value)
        if name == 'position':
            if self.position.player_idx < 0:
                # invalid position, do not update skill positions
                return
            for skill in self.skills:
                skill.position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    charactor_idx = self.position.charactor_idx,
                    area = ObjectPositionType.SKILL,
                    id = skill.id,
                )

    def _init_skills(self) -> None:
        """
        Initialize skills. It will be called in __init__.
        """
        raise NotImplementedError

    @property
    def is_defeated(self) -> bool:
        return not self.is_alive

    @property
    def is_stunned(self) -> bool:
        """
        Check if the charactor is stunned.
        """
        stun_status_names = [
            'Frozen',
            'Petrification',
            'Mist Bubble',
            'Stun',
        ]
        for status in self.status:
            if status.name in stun_status_names:
                return True
        return False

    @property
    def damage_taken(self) -> int:
        """
        Get damage taken by the charactor.
        """
        return self.max_hp - self.hp

    def get_object_lists(self) -> List[ObjectBase]:
        """
        Get all objects of the charactor, order is passive skill, weapon, 
        artifact, talent, status. For status, order is their index in status 
        list, i.e. generated time.
        """
        result: List[ObjectBase] = [self]
        for skill in self.skills:
            result.append(skill)
        if self.weapon is not None:
            result.append(self.weapon)
        if self.artifact is not None:
            result.append(self.artifact)
        if self.talent is not None:
            result.append(self.talent)
        result += self.status
        return result

    def get_object(self, position: ObjectPosition) -> ObjectBase | None:
        """
        Get object by its position. If obect not exist, return None.
        """
        if position.area == ObjectPositionType.CHARACTOR_STATUS:
            for status in self.status:
                if status.id == position.id:
                    return status
            return None
        elif position.area == ObjectPositionType.SKILL:
            for skill in self.skills:
                if skill.id == position.id:
                    return skill
            raise AssertionError('Skill not found')
        else:
            assert position.area == ObjectPositionType.CHARACTOR
            if self.id == position.id:
                return self
            elif self.talent is not None and self.talent.id == position.id:
                return self.talent
            elif self.weapon is not None and self.weapon.id == position.id:
                return self.weapon
            elif self.artifact is not None and self.artifact.id == position.id:
                return self.artifact
            raise NotImplementedError('Not tested part')
            return None
