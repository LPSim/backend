from typing import Any, List, Literal

from ...struct import Cost, ObjectPosition

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageValue
)

from ...consts import (
    CostLabels, DamageElementalType, DamageType, ElementType, 
    ElementalReactionType, IconType, ObjectPositionType, SkillType
)

from ...action import (
    Actions, ChangeObjectUsageAction, CreateObjectAction, MakeDamageAction, 
    RemoveObjectAction
)

from ...event import (
    AfterMakeDamageEventArguments, ReceiveDamageEventArguments, 
    RoundEndEventArguments, SkillEndEventArguments
)
from .base import (
    CharactorStatusBase, ElementalInfusionCharactorStatus, UsageCharactorStatus
)


class SeedOfSkandha(UsageCharactorStatus):
    name: Literal['Seed of Skandha'] = 'Seed of Skandha'
    desc: str = (
        'After a character who has a Seed of Skandha takes Elemental Reaction '
        'DMG: Deals 1 Piercing DMG to the character(s) to which the '
        'Seed of Skandha is attached to on the same side of the field. '
        'Usage(s): 2'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        Only seed of charactor received the damage will trigger event, it will
        check all charactor status and trigger them and call ChangeObjectUsage.
        """
        damage_value = event.final_damage
        if damage_value.damage_type != DamageType.DAMAGE:
            # not damage, not trigger
            return []
        if damage_value.element_reaction == ElementalReactionType.NONE:
            # not elemental reaction, not trigger
            return []
        if not self.position.check_position_valid(
            damage_value.target_position, match, 
            player_idx_same = True, charactor_idx_same = True,
        ):
            # damage not received by self, not trigger
            return []
        assert self.usage > 0
        # trigger, check all seed on the same side
        actions: List[MakeDamageAction | ChangeObjectUsageAction] = []
        table = match.player_tables[self.position.player_idx]
        has_pyro_charactor = False
        has_talent = False
        # check if enemy has pyro charactor and has talent nahida
        for charactor in match.player_tables[
                1 - self.position.player_idx].charactors:
            if charactor.element == ElementType.PYRO:
                has_pyro_charactor = True
            if charactor.name == 'Nahida':
                if charactor.talent is not None:
                    has_talent = True
        for charactor in table.charactors:
            for status in charactor.status:
                if status.name == 'Seed of Skandha':
                    # found a seed, trigger it
                    assert status.usage > 0
                    d_ele_type = DamageElementalType.PIERCING
                    if has_pyro_charactor and has_talent:
                        # enemy have talent nahida and pyro, dendeo damage
                        d_ele_type = DamageElementalType.DENDRO
                    # change usage first, so no need to claim new trigger
                    actions.append(ChangeObjectUsageAction(
                        object_position = status.position,
                        change_type = 'DELTA',
                        change_usage = -1,
                    ))
                    actions.append(MakeDamageAction(
                        source_player_idx = self.position.player_idx,
                        target_player_idx = self.position.player_idx,
                        damage_value_list = [
                            DamageValue(
                                position = status.position,
                                damage = 1,
                                target_position = charactor.position,
                                damage_type = DamageType.DAMAGE,
                                cost = Cost(),
                                damage_elemental_type = d_ele_type,
                            )
                        ],
                    ))
        return actions


class VijnanaSuffusion(ElementalInfusionCharactorStatus, UsageCharactorStatus):
    name: Literal['Vijnana Suffusion'] = 'Vijnana Suffusion'
    desc: str = (
        'When the character to which this is attached to uses a Charged '
        'Attack: Their Physical DMG dealt will be converted to Dendro DMG and '
        'after skill DMG is finalized, summon 1 Clusterbloom Arrow.'
    )
    version: Literal['3.6'] = '3.6'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.DENDRO

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        When character use charged attack, change damage type to dendro
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not use normal attack
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode)

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If talent equipped, and is charged attack, decrease 1 any cost
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.talent is None:
            # no talent, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not this charactor use skill, not modify
            return value
        if not (
            match.player_tables[self.position.player_idx].charge_satisfied
            and value.cost.label & CostLabels.NORMAL_ATTACK.value != 0
        ):
            # not charged attack, not modify
            return value
        # decrease
        value.cost.decrease_cost(None)
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction | RemoveObjectAction]:
        """
        If self use charged attack, summon Clusterbloom Arrow
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not same player or charactor, or not skill, not modify
            return []
        if not (
            match.player_tables[self.position.player_idx].charge_satisfied
            and match.get_object(event.action.position).skill_type
            == SkillType.NORMAL_ATTACK
        ):
            # not charged attack, not modify
            return []
        assert self.usage > 0
        # summon
        self.usage -= 1
        return [CreateObjectAction(
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.SUMMON,
                id = 0
            ),
            object_name = 'Clusterbloom Arrow',
            object_arguments = {}
        )] + self.check_should_remove()


class RadicalVitality(CharactorStatusBase):
    name: Literal['Radical Vitality'] = 'Radical Vitality'
    desc: str = ''
    desc_template: str = (
        'When this character deals or takes Elemental DMG: Gain 1 stack of '
        'Radical Vitality. (Max XXX stacks) '
        'End Phase: If Radical Vitality stacks reach maximum, they will be '
        'cleared and the character will lose all Energy.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 0
    max_usage: int = 3
    element_damage_triggered: bool = False
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._update_desc()

    def _update_desc(self) -> None:
        self.desc = self.desc_template.replace(
            'XXX', str(self.max_usage)
        )

    def renew(self, new_status: 'RadicalVitality') -> None:
        super().renew(new_status)
        self._update_desc()

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[Actions]:
        if self.usage == self.max_usage:
            self.usage = 0
        return []

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If contains elemental damage and target or source self, gain progress
        """
        satisfied: bool = False
        for damage in event.damages:
            source_self = self.position.check_position_valid(
                damage.final_damage.position, match, 
                player_idx_same = True, charactor_idx_same = True,
            )
            target_self = self.position.check_position_valid(
                damage.final_damage.target_position, match, 
                player_idx_same = True, charactor_idx_same = True,
            )
            if source_self or target_self:
                # source or target self
                if damage.final_damage.damage_type != DamageType.DAMAGE:
                    # heal, do nothing
                    continue
                if (
                    damage.final_damage.damage_elemental_type in [
                        DamageElementalType.PHYSICAL, 
                        DamageElementalType.PIERCING,
                        DamageElementalType.HEAL
                    ]
                ):
                    # physical or piercing or heal, do nothing
                    continue
                if source_self and (
                    damage.final_damage.cost.label 
                    & CostLabels.ELEMENTAL_BURST.value != 0
                ):
                    # source self, and elemental burst, do nothing
                    continue
                satisfied = True
        if satisfied:
            # increase usage
            self.usage = min(self.usage + 1, self.max_usage)
        return []


DendroCharactorStatus = SeedOfSkandha | VijnanaSuffusion | RadicalVitality
