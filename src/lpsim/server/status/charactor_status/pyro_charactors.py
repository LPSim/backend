from typing import Any, List, Literal

from ....utils.class_registry import register_class
from ...struct import Cost

from ...action import (
    ActionTypes, Actions, CreateObjectAction, DrawCardAction, MakeDamageAction,
    RemoveObjectAction
)

from ...event import (
    MakeDamageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments
)

from ...consts import (
    DamageElementalType, DamageType, DieColor, IconType, ObjectPositionType, 
    SkillType
)

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue, DamageValue
)
from .base import (
    DefendCharactorStatus, ElementalInfusionCharactorStatus, 
    PrepareCharactorStatus, ReviveCharactorStatus, RoundCharactorStatus, 
    RoundEndAttackCharactorStatus, ShieldCharactorStatus, UsageCharactorStatus
)


class Stealth_3_3(DefendCharactorStatus, ElementalInfusionCharactorStatus):
    name: Literal['Stealth'] = 'Stealth'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    infused_elemental_type: DamageElementalType = DamageElementalType.PYRO

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, and has talent, change physical to pyro
        """
        assert mode == 'REAL'
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.talent is None:
            # no talent, do nothing
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode
        )

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When self use skill, increase damage by 1
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use damage skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        # increase damage by 1
        value.damage += 1
        self.usage -= 1
        return value


class ExplosiveSpark_3_4(UsageCharactorStatus):
    name: Literal['Explosive Spark'] = 'Explosive Spark'
    version: Literal['3.4'] = '3.4'
    usage: int
    max_usage: int
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        # modify damage
        assert self.usage > 0
        self.usage -= 1
        value.damage += 1
        return value

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If self use charged attack, decrease one 
        unaligned die cost.
        """
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not this charactor use skill, not modify
            return value
        skill = match.get_object(value.position)
        skill_type: SkillType = skill.skill_type
        if skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack, not modify
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        # try decrease pyro cost
        value.cost.decrease_cost(DieColor.PYRO)
        return value


class NiwabiEnshou_3_3(ElementalInfusionCharactorStatus, UsageCharactorStatus):
    name: Literal['Niwabi Enshou'] = 'Niwabi Enshou'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.PYRO
    icon_type: Literal[IconType.ATK_UP_FIRE] = IconType.ATK_UP_FIRE

    effect_triggered: bool = False

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If corresponding charactor use normal attack, increase damage by 1,
        and mark effect triggered.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        # this charactor use normal attack, modify
        self.usage -= 1
        self.effect_triggered = True
        value.damage += 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        do not remove immediately here, as may trigger additional attack at
        skill end.
        """
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If effect triggered, and have talent on yoimiya, make 1 pyro damage.
        If usage is zero, then remove self.
        """
        ret: List[MakeDamageAction | RemoveObjectAction] = []
        if self.position.player_idx != event.action.position.player_idx:
            # not self player use skill
            self.effect_triggered = False
            return list(self.check_should_remove())
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if (
            charactor.name == 'Yoimiya'
            and event.action.skill_type == SkillType.NORMAL_ATTACK
            and self.effect_triggered
            and charactor.talent is not None
        ):
            # yoimiya use normal attack and self effect triggered
            # and has talent, attack 1 pyro damage
            target = match.player_tables[
                1 - self.position.player_idx].get_active_charactor()
            ret.append(MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target.position,
                        damage = 1,
                        damage_elemental_type = DamageElementalType.PYRO,
                        cost = Cost(),
                    )
                ]
            ))
        # reset mark
        self.effect_triggered = False
        return ret + self.check_should_remove()


class Brilliance_3_8(RoundCharactorStatus):
    name: Literal['Brilliance'] = 'Brilliance'
    version: Literal['3.8'] = '3.8'
    usage: int = 2
    max_usage: int = 2

    decrease_cost_usage: int = 1
    decrease_cost_max_usage: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def renew(self, new_status: 'Brilliance_3_8') -> None:
        self.decrease_cost_usage = max(new_status.decrease_cost_usage, 
                                       self.decrease_cost_usage)
        self.decrease_cost_max_usage = max(new_status.decrease_cost_max_usage, 
                                           self.decrease_cost_max_usage)
        return super().renew(new_status)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.decrease_cost_usage = self.decrease_cost_max_usage
        return super().event_handler_ROUND_PREPARE(event, match)

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        if self.decrease_cost_usage <= 0:
            # no usage left
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charge attack
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL
        ):
            # not self use skill
            return value
        skill = match.get_object(value.position)
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return value
        # decrease cost
        if value.cost.decrease_cost(DieColor.PYRO):  # pragma: no branch
            if mode == 'REAL':
                self.decrease_cost_usage -= 1
        return value

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        return [CreateObjectAction(
            object_name = 'Scarlet Seal',
            object_position = self.position,
            object_arguments = {}
        )]


class ScarletSeal_4_2(UsageCharactorStatus):
    name: Literal['Scarlet Seal'] = 'Scarlet Seal'
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 2
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP
    triggered: bool = False

    available_handler_in_trashbin: List[ActionTypes] = [
        ActionTypes.SKILL_END
    ]

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not self use normal attack
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charge attack
            return value
        # increase damage
        assert mode == 'REAL'
        self.usage -= 1
        self.triggered = True
        value.damage += 2
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[DrawCardAction]:
        """
        When triggered, and self charactor have talent, talent need to draw,
        then draw one card.
        """
        if not self.triggered:
            # not triggered
            return []
        self.triggered = False
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.talent is not None and charactor.talent.draw_card:
            # have talent and need draw
            return [DrawCardAction(
                player_idx = self.position.player_idx,
                number = 1,
                draw_if_filtered_not_enough = True
            )]
        return []


class ParamitaPapilio_3_7(ElementalInfusionCharactorStatus, 
                          RoundCharactorStatus):
    name: Literal['Paramita Papilio'] = 'Paramita Papilio'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    infused_elemental_type: DamageElementalType = DamageElementalType.PYRO

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self use damage skill
            return value
        if (
            value.damage_elemental_type != DamageElementalType.PYRO
        ):  # pragma: no cover
            # not pyro damage
            return value
        # increase damage
        value.damage += 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If self use charged attack, create blood blossom on target
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL
        ):
            # not self use skill
            return []
        if not (
            event.action.skill_type == SkillType.NORMAL_ATTACK
            and match.player_tables[self.position.player_idx].charge_satisfied
        ):
            # not charged attack
            return []
        return [CreateObjectAction(
            object_position = event.action.target_position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_name = 'Blood Blossom',
            object_arguments = {}
        )]


class BloodBlossom_3_7(RoundEndAttackCharactorStatus):
    name: Literal['Blood Blossom'] = 'Blood Blossom'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.DOT] = IconType.DOT
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO


class DilucInfusion_3_3(ElementalInfusionCharactorStatus, 
                        RoundCharactorStatus):
    name: Literal['Pyro Elemental Infusion'] = 'Pyro Elemental Infusion'
    mark: Literal['Diluc'] = 'Diluc'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2


class FieryRebirth_3_7(ReviveCharactorStatus):
    name: Literal['Fiery Rebirth'] = 'Fiery Rebirth'
    version: Literal['3.7'] = '3.7'
    heal: int = 3


class AegisOfAbyssalFlame_3_7(ShieldCharactorStatus):
    name: Literal['Aegis of Abyssal Flame'] = 'Aegis of Abyssal Flame'
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 3

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if (
            value.is_corresponding_charactor_use_damage_skill(
                self.position, match, None
            )
            and value.damage_elemental_type == DamageElementalType.PYRO
        ):
            # self attack and pyro damage, increase 1 damage
            assert mode == 'REAL'
            value.damage += 1
        return value


class IncinerationDrive_4_1(PrepareCharactorStatus):
    name: Literal['Incineration Drive'] = 'Incineration Drive'
    version: Literal['4.1'] = '4.1'
    charactor_name: Literal['Dehya'] = 'Dehya'
    skill_name: Literal['Incineration Drive'] = 'Incineration Drive'


class ScarletSeal_3_8(ScarletSeal_4_2):
    version: Literal['3.8']
    usage: int = 1
    max_usage: int = 1


register_class(
    Stealth_3_3 | ExplosiveSpark_3_4 | NiwabiEnshou_3_3 | Brilliance_3_8 
    | ScarletSeal_4_2 | ParamitaPapilio_3_7 | BloodBlossom_3_7 
    | DilucInfusion_3_3 | FieryRebirth_3_7 | AegisOfAbyssalFlame_3_7 
    | IncinerationDrive_4_1 | ScarletSeal_3_8
)
