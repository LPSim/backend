from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import CostValue, DamageIncreaseValue, DamageValue

from ...struct import Cost, ObjectPosition

from ...consts import (
    CostLabels, DamageElementalType, DamageType, IconType, ObjectPositionType, 
    SkillType
)

from ...action import (
    ActionTypes, Actions, CreateObjectAction, MakeDamageAction, 
    RemoveObjectAction
)

from ...event import (
    CharactorDefeatedEventArguments, CreateObjectEventArguments, 
    MakeDamageEventArguments, RoundPrepareEventArguments, 
    SkillEndEventArguments
)
from .base import (
    CharactorStatusBase, ElementalInfusionCharactorStatus, 
    PrepareCharactorStatus, RoundCharactorStatus, 
    RoundEndAttackCharactorStatus, ShieldCharactorStatus, UsageCharactorStatus
)


class Riptide_4_1(CharactorStatusBase):
    """
    This status will not deal damages directly, and defeat-regenerate is 
    handled by system handler, which is created by Tartaglia'is passive skill
    when game starts.
    """
    name: Literal['Riptide'] = 'Riptide'
    # As Riptide has changed, all status it related to should have different
    # version. To avoid using wrong version of status, related status have
    # not default value.
    version: Literal['4.1']
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    available_handler_in_trashbin: List[ActionTypes] = [
        ActionTypes.CHARACTOR_DEFEATED
    ]

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If defeated charactor has Riptide, the next active charactor will get
        Riptide. As this event triggers later than CHOOSE_CHARACTOR, current
        active charactor is set.
        """
        pidx = event.action.player_idx
        cidx = event.action.charactor_idx
        if (
            pidx != self.position.player_idx 
            or cidx != self.position.charactor_idx
        ):
            # defeated charactor not self charactor
            return []
        return [CreateObjectAction(
            object_name = 'Riptide',
            object_position = ObjectPosition(
                player_idx = pidx,
                area = ObjectPositionType.CHARACTOR_STATUS,
                charactor_idx = match.player_tables[pidx].active_charactor_idx,
                id = 0
            ),
            object_arguments = { 'version': self.version }
        )]


class RangedStance_4_1(CharactorStatusBase):
    name: Literal['Ranged Stance'] = 'Ranged Stance'
    # As Riptide has changed, all status it related to should have different
    # version. To avoid using wrong version of status, related status have
    # not default value.
    version: Literal['4.1']
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS
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
            object_arguments = { 'version': self.version }
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


class MeleeStance_4_1(ElementalInfusionCharactorStatus,
                      RoundCharactorStatus):
    name: Literal['Melee Stance'] = 'Melee Stance'
    # As Riptide has changed, all status it related to should have different
    # version. To avoid using wrong version of status, related status have
    # not default value.
    version: Literal['4.1']
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS
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
                    object_arguments = { 'version': self.version }
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
                    object_arguments = { 'version': self.version }
                )
            )
        return ret


class Riptide_3_7(Riptide_4_1, RoundCharactorStatus):
    """
    This status will not deal damages directly, and defeat-regenerate is 
    handled by system handler, which is created by Tartaglia'is passive skill
    when game starts.
    """
    name: Literal['Riptide'] = 'Riptide'
    version: Literal['3.7']
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS


class RangedStance_3_7(RangedStance_4_1):
    version: Literal['3.7']


class MeleeStance_3_7(MeleeStance_4_1):
    version: Literal['3.7']


class CeremonialGarment_3_5(RoundCharactorStatus):
    name: Literal['Ceremonial Garment'] = 'Ceremonial Garment'
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

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


class HeronShield_3_8(ShieldCharactorStatus, PrepareCharactorStatus):
    name: Literal['Heron Shield'] = 'Heron Shield'
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


class Refraction_3_3(RoundCharactorStatus):
    name: Literal['Refraction'] = 'Refraction'
    desc: Literal['', 'talent'] = ''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2

    is_talent_activated: bool = False
    cost_increase_usage: int = 1
    cost_increase_max_usage: int = 1
    icon_type: Literal[IconType.DEBUFF] = IconType.DEBUFF

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.is_talent_activated:
            self.desc = 'talent'

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.cost_increase_usage = self.cost_increase_max_usage
        return super().event_handler_ROUND_PREPARE(event, match)

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        if talent activated, increase switch cost
        """
        if (
            self.is_talent_activated
            and self.cost_increase_usage > 0
            and value.cost.label & CostLabels.SWITCH_CHARACTOR.value != 0
            and value.position.player_idx == self.position.player_idx
            and value.position.charactor_idx == self.position.charactor_idx
        ):
            # talent activated, switch cost, and this charactor switch to
            # other, increase cost
            value.cost.any_dice_number += 1
            if mode == 'REAL':
                self.cost_increase_usage -= 1
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if value.damage_elemental_type != DamageElementalType.HYDRO:
            # not hydro damage
            return value
        if value.is_corresponding_charactor_receive_damage(
            self.position, match
        ):
            # this charactor receive damage
            value.damage += 1
        return value


class TakimeguriKanka_4_1(ElementalInfusionCharactorStatus, 
                          UsageCharactorStatus):
    name: Literal['Takimeguri Kanka'] = 'Takimeguri Kanka'
    version: Literal['4.1'] = '4.1'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    icon_type: Literal[IconType.ATK_UP_WATER] = IconType.ATK_UP_WATER

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            assert mode == 'REAL'
            self.usage -= 1
            value.damage += 1
            charactor = match.player_tables[
                self.position.player_idx].charactors[
                    self.position.charactor_idx]
            target = match.player_tables[
                value.target_position.player_idx].charactors[
                    value.target_position.charactor_idx]
            if (
                charactor.talent is not None
                and target.hp <= 6
            ):
                value.damage += 1
        return value


class LingeringAeon_4_2(RoundEndAttackCharactorStatus):
    name: Literal['Lingering Aeon'] = 'Lingering Aeon'
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 1
    damage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS


register_class(
    Riptide_4_1 | RangedStance_4_1 | MeleeStance_4_1 
    | Riptide_3_7 | RangedStance_3_7 | MeleeStance_3_7 
    | CeremonialGarment_3_5 | HeronShield_3_8
    | Refraction_3_3 | TakimeguriKanka_4_1 | LingeringAeon_4_2
)
