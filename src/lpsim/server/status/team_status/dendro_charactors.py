from typing import Any, List, Literal

from ...action import (
    Actions, ChangeObjectUsageAction, MakeDamageAction, RemoveObjectAction
)
from ...event import (
    CreateObjectEventArguments, ReceiveDamageEventArguments, 
    SkillEndEventArguments
)
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, ElementType, ElementalReactionType, 
    ObjectPositionType
)

from ...modifiable_values import DamageIncreaseValue, DamageValue
from .base import RoundTeamStatus


class ShrineOfMaya(RoundTeamStatus):
    name: Literal['Shrine of Maya'] = 'Shrine of Maya'
    desc: str = (
        'When your character triggers an Elemental Reaction: +1 Additional '
        'DMG.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2

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
                                    change_type = 'DELTA',
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


class FloralSidewinder(RoundTeamStatus):
    """
    Damage made on skill end, but need to check whether dendro reaction made
    before.
    """
    name: Literal['Floral Sidewinder'] = 'Floral Sidewinder'
    desc: str = (
        "during this Round, when your characters' Skills trigger "
        "Dendro-Related Reactions: Deal 1 Dendro DMG. (Once per Round)"
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    dendro_reaction_made: bool = False

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
                source_player_idx = self.position.player_idx,
                target_player_idx = 1 - self.position.player_idx,
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


DendroTeamStatus = ShrineOfMaya | FloralSidewinder
