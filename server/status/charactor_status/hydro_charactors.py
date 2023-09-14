from typing import Any, List, Literal

from ...modifiable_values import DamageIncreaseValue, DamageValue

from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, ObjectPositionType, SkillType
)

from ...action import (
    ActionTypes, Actions, CreateObjectAction, MakeDamageAction, 
    RemoveObjectAction
)

from ...event import (
    CreateObjectEventArguments, MakeDamageEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments
)
from .base import (
    CharactorStatusBase, ElementalInfusionCharactorStatus, 
    PrepareCharactorStatus, RoundCharactorStatus, ShieldCharactorStatus
)


class Riptide(RoundCharactorStatus):
    """
    This status will not deal damages directly, and defeat-regenerate is 
    handled by system handler, which is created by Tartaglia'is passive skill
    when game starts.
    """
    name: Literal['Riptide'] = 'Riptide'
    desc: str = (
        'When the character to which this is attached is defeated: Apply '
        'Riptide to active character. '
        'When Tartaglia is in Melee Stance, he will deal additional DMG when '
        'attacking the character to which this is attached.'
    )
    desc_virtual: str = (
        'Virtual Riptide which will be applied to all allies when charactor '
        'defeated with Riptide. After choosing active charactor, the virtual '
        'will attach real Riptide for active charactor, and all virtual '
        'Riptide will be removed.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2


class RangedStance(CharactorStatusBase):
    name: Literal['Ranged Stance'] = 'Ranged Stance'
    desc: str = (
        'After the character to which this is attached uses Charged Attack: '
        'Apply Riptide to target character.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When self charactor use charged attack, apply Riptide to target 
        character.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not self charactor use skill
            return []
        skill = match.get_object(event.action.position)
        if (
            not match.player_tables[self.position.player_idx].charge_satisfied
            or skill.skill_type != SkillType.NORMAL_ATTACK
        ):
            # not charged attack
            return []
        charactor = match.player_tables[
            event.action.target_position.player_idx].charactors[
                event.action.target_position.charactor_idx]
        if charactor.is_defeated:
            # defeated charactor cannot attach Riptide
            return []
        return [CreateObjectAction(
            object_name = 'Riptide',
            object_position = event.action.target_position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = {}
        )]

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        If self charactor gain Melee Stance, remove this status.
        """
        if (
            event.action.object_name == 'Melee Stance'
            and self.position.check_position_valid(
                event.action.object_position, match, player_idx_same = True,
                charactor_idx_same = True, 
                target_area = ObjectPositionType.CHARACTOR_STATUS,
            )
        ):
            # self charactor gain melee stance, remove this status
            return [RemoveObjectAction(
                object_position = self.position
            )]
        return []


class MeleeStance(ElementalInfusionCharactorStatus,
                  RoundCharactorStatus):
    name: Literal['Melee Stance'] = 'Melee Stance'
    buff_desc: str = (
        'Physical DMG dealt by character is converted to Hydro DMG. '
        'After the character uses Charged Attack: Apply Riptide to target '
        'character. Character deals +1 DMG to target characters with Riptide '
        'attached. '
        'After Skills are used against characters affected by Riptide: '
        'Deal 1 Piercing DMG to the next opposing off-field character. '
        '(Twice per Round)'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.HYDRO

    extra_attack_usage: int = 2
    extra_attack_max_usage: int = 2

    def self_skill(self, position: ObjectPosition, match: Any) -> bool:
        """
        Whether position is self skill
        """
        return self.position.check_position_valid(
            position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        )

    def charge_attack(self, skill_position: ObjectPosition, 
                      match: Any) -> bool:
        """
        Whether position is charged attack
        """
        skill = match.get_object(skill_position)
        return (
            match.player_tables[skill_position.player_idx].charge_satisfied
            and skill.skill_type == SkillType.NORMAL_ATTACK
        )

    def opposite_active_has_riptide(self, match: Any) -> bool:
        """
        Whether opposite active charactor has Riptide
        """
        active = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        for status in active.status:
            if status.name == 'Riptide':
                return True
        return False

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If target has Riptide, increase damage by 1
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not this charactor use skill, not modify
            return value
        if not self.opposite_active_has_riptide(match):
            # opposite active charactor does not have Riptide
            return value
        # add damage
        value.damage += 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When use skill on target with Riptide, deal 1 piercing damage to next
        charactor.
        """
        assert len(event.damages) > 0
        # first must be skill damage
        damage = event.damages[0]
        target_position = damage.final_damage.target_position
        if not self.self_skill(damage.final_damage.position, match):
            # not self charactor use skill
            return []
        if self.opposite_active_has_riptide(match):
            # opposite have Riptide, deal 1 piercing damage to next charactor
            next_idx = match.player_tables[
                1 - self.position.player_idx].next_charactor_idx(
                    target_position.charactor_idx)
            if next_idx is not None and self.extra_attack_usage > 0:
                # has next charactor and has usage:
                charactor = match.player_tables[
                    1 - self.position.player_idx].charactors[next_idx]
                self.extra_attack_usage -= 1
                return [MakeDamageAction(
                    source_player_idx = self.position.player_idx,
                    target_player_idx = 1 - self.position.player_idx,
                    damage_value_list = [
                        DamageValue(
                            position = self.position,
                            damage_type = DamageType.DAMAGE,
                            target_position = charactor.position,
                            damage = 1,
                            damage_elemental_type 
                            = DamageElementalType.PIERCING,
                            cost = Cost(),
                        )
                    ]
                )]
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        """
        When self charactor use charged attack, apply Riptide to target 
        character.
        """
        ret: List[CreateObjectAction | MakeDamageAction] = []

        if not self.self_skill(event.action.position, match):
            # not self charactor use skill
            return []
        # Riptide attach conditions
        if self.charge_attack(event.action.position, match):
            # charged attack
            charactor = match.player_tables[
                event.action.target_position.player_idx].charactors[
                    event.action.target_position.charactor_idx]
            if charactor.is_alive:
                ret += [CreateObjectAction(
                    object_name = 'Riptide',
                    object_position = event.action.target_position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS),
                    object_arguments = {}
                )]

        return ret

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset extra attack usage, and when this status is removed, 
        attach Ranged Stance.
        """
        self.extra_attack_usage = self.extra_attack_max_usage
        ret = super().event_handler_ROUND_PREPARE(event, match)
        if len(ret) > 0:
            # has remove action
            assert ret[0].type == ActionTypes.REMOVE_OBJECT
            ret.append(
                CreateObjectAction(
                    object_name = 'Ranged Stance',
                    object_position = self.position,
                    object_arguments = {}
                )
            )
        return ret


class CeremonialGarment(RoundCharactorStatus):
    name: Literal['Ceremonial Garment'] = 'Ceremonial Garment'
    desc: str = (
        'The character to which this is attached has their Normal Attacks '
        'deal +1 DMG. After the character to which this attached uses a '
        'Normal Attack: Heal 1 HP for all your characters.'
    )
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If self use normal attack, increase damage by 1.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        # damage +1
        value.damage += 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self use normal attack, heal all our charactors for 1 HP.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not self use skill
            return []
        skill = match.get_object(event.action.position)
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return []
        action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = []
        )
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if charactor.is_alive:
                action.damage_value_list.append(DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                ))
        return [action]


class HeronShield(PrepareCharactorStatus, ShieldCharactorStatus):
    name: Literal['Heron Shield'] = 'Heron Shield'
    desc: str = (
        'The next time this character acts, they will immediately use the '
        'Skill Heron Strike. While preparing this Skill: Grant 2 Shield '
        'points to the character to which this is attached.'
    )
    version: Literal['3.8'] = '3.8'
    charactor_name: Literal['Candace'] = 'Candace'
    skill_name: Literal['Heron Strike'] = 'Heron Strike'

    usage: int = 2
    max_usage: int = 2

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        Do not remove when usage becomes zero
        """
        return []


HydroCharactorStatus = (
    Riptide | RangedStance | MeleeStance | CeremonialGarment | HeronShield
)
