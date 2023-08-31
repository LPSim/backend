

from typing import Any, Literal

from ...struct import DamageValue

from ...consts import (
    DamageElementalType, DamageType, ElementType, ElementalReactionType
)

from ...action import ChangeObjectUsageAction, MakeDamageAction

from ...event import ReceiveDamageEventArguments
from .base import UsageCharactorStatus


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

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> list[MakeDamageAction | ChangeObjectUsageAction]:
        """
        Only seed of charactor received the damage will trigger event, it will
        check all charactor status and trigger them and call ChangeObjectUsage.
        """
        damage_value = event.final_damage
        if damage_value.damage_type != DamageType.DAMAGE:
            # not damage, not trigger
            raise NotImplementedError('Not tested part')
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
        actions: list[MakeDamageAction | ChangeObjectUsageAction] = []
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
                                damage_type = DamageType.DAMAGE,
                                charge_cost = 0,
                                target_player = 'CURRENT',
                                target_charactor = 'ABSOLUTE',
                                damage_elemental_type = d_ele_type,

                                target_charactor_idx = 
                                status.position.charactor_idx,
                            )
                        ],
                    ))
        return actions


DendroCharactorStatus = SeedOfSkandha | SeedOfSkandha
