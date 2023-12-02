from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import (
    Actions, ChangeObjectUsageAction, CreateObjectAction, MakeDamageAction, 
    RemoveObjectAction
)
from ...event import (
    CreateObjectEventArguments, MakeDamageEventArguments, 
    ReceiveDamageEventArguments, RoundPrepareEventArguments, 
    SkillEndEventArguments
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, ElementType, ElementalReactionType, 
    IconType, ObjectPositionType
)

from ...modifiable_values import DamageIncreaseValue, DamageValue
from .base import RoundTeamStatus, ShieldTeamStatus, SwitchActionTeamStatus


class ShrineOfMaya_3_7(RoundTeamStatus):
    name: Literal['Shrine of Maya'] = 'Shrine of Maya'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        When self is created, check whether to increase the usage of Seed of
        Skandha.
        """
        if event.action.object_name != 'Shrine of Maya':
            # not creating Shrine of Maya, do nothing.
            return []
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        assert active_charactor is not None
        if (
            active_charactor.name == 'Nahida' 
            and active_charactor.talent is not None
        ):
            # talent equipped, check if have electro charactor.
            has_electro_charactor = False
            for charactor in match.player_tables[
                    self.position.player_idx].charactors:
                if charactor.element == ElementType.ELECTRO:
                    has_electro_charactor = True
                    break
            if has_electro_charactor:
                # has electro charactor, add one usage for enemy
                # Seed of Skandha.
                ret = []
                for charactor in match.player_tables[
                        1 - self.position.player_idx].charactors:
                    for status in charactor.status:
                        if status.name == 'Seed of Skandha':
                            position = status.position.set_area(
                                ObjectPositionType.CHARACTOR_STATUS)
                            ret.append(
                                ChangeObjectUsageAction(
                                    object_position = position,
                                    change_usage = 1,
                                )
                            )
                return ret
        return []

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        +1 on self elemental reaction damage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if value.target_position.player_idx == self.position.player_idx:
            # attack self, not activate
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self, not activate
            return value
        if value.element_reaction is not ElementalReactionType.NONE:
            value.damage += 1
        return value


class FloralSidewinder_3_3(RoundTeamStatus):
    """
    Damage made on skill end, but need to check whether dendro reaction made
    before.
    """
    name: Literal['Floral Sidewinder'] = 'Floral Sidewinder'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    dendro_reaction_made: bool = False
    icon_type: Literal[IconType.ATK_SELF] = IconType.ATK_SELF

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        Check whether dendro reaction made.
        """
        damage = event.final_damage
        if not damage.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self charactor made damage
            return []
        if ElementType.DENDRO not in damage.reacted_elements:
            # not dendro reaction
            return []
        # mark dendro reaction made
        self.dendro_reaction_made = True
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        if no dendro reaction made, return. otherwise, reset dendro reaction
        made, and if our active charactor use skill, deal 1 dendro damage.
        """
        if not self.dendro_reaction_made:
            # no dendro reaction made
            return []
        # regardless of the following conditions, reset dendro reaction made
        self.dendro_reaction_made = False
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if not event.action.position.check_position_valid(  # pragma: no cover
            charactor.position, match, player_idx_same = True,
            charactor_idx_same = True, source_area = ObjectPositionType.SKILL
        ):
            # not this charactor use skill
            return []  # pragma: no cover
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        self.usage -= 1
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target.position,
                        damage = 1,
                        damage_elemental_type = DamageElementalType.DENDRO,
                        cost = Cost()
                    )
                ]
            )
        ] + self.check_should_remove()


class AdeptalLegacy_4_1(SwitchActionTeamStatus):
    name: Literal['Adeptal Legacy'] = 'Adeptal Legacy'
    version: Literal['4.1'] = '4.1'
    usage: int = 3
    max_usage: int = 3
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def _action(self, match: Any) -> List[Actions]:
        """
        attack enemy active charactor and heal our active charactor.
        """
        enemy_active_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        our_active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = enemy_active_charactor.position,
                        damage = 1,
                        damage_elemental_type = DamageElementalType.DENDRO,
                        cost = Cost()
                    )
                ]
            ),
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = our_active_charactor.position,
                        damage = -1,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = Cost()
                    )
                ]
            ),
        ]


class PulsingClarity_4_2(RoundTeamStatus):
    name: Literal['Pulsing Clarity'] = 'Pulsing Clarity'
    version: Literal['4.2'] = '4.2'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        ret = super().event_handler_ROUND_PREPARE(event, match)
        return [
            CreateObjectAction(
                object_name = 'Seamless Shield',
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = 0
                ),
                object_arguments = {}
            )
        ] + ret


class SeamlessShield_4_2(ShieldTeamStatus):
    name: Literal['Seamless Shield'] = 'Seamless Shield'
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 1
    remove_triggered: bool = False

    def effect_action(self, match: Any) -> MakeDamageAction:
        """
        make damage and heal
        """
        our_active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        opposite_active_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        ret = MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = opposite_active_charactor.position,
                    damage = 1,
                    damage_elemental_type = DamageElementalType.DENDRO,
                    cost = Cost()
                ),
            ],
        )
        if our_active_charactor.hp > 0:
            # when active charactor has no hp, no need to heal
            ret.damage_value_list.append(
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = our_active_charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                ),
            )
        return ret

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        if not self.position.check_position_valid(
            event.action.object_position, match, player_idx_same = True,
            area_same = True,
        ):
            # not create on our area
            return []
        if (
            event.action.object_name != self.name
            or event.create_result != 'RENEW'
        ):
            # not create ourself, or not renew create
            return []
        # renew, make damage and heal
        return [self.effect_action(match)]

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        When damage made, check whether the team status should be removed.
        """
        if self.remove_triggered:
            # already triggered, do nothing
            return []
        ret = self.check_should_remove()
        if len(ret) > 0:
            # should remove, remove self, then make damage and heal
            self.remove_triggered = True
            return [
                self.effect_action(match),
                RemoveObjectAction(object_position = self.position),
            ]
        return list(ret)


register_class(
    ShrineOfMaya_3_7 | FloralSidewinder_3_3 | AdeptalLegacy_4_1 
    | PulsingClarity_4_2 | SeamlessShield_4_2
)
