
from typing import Any, List, Literal

from ...struct import Cost

from ...consts import DamageElementalType, DamageType

from ...modifiable_values import DamageValue

from ...action import MakeDamageAction

from ...event import PlayerActionStartEventArguments
from .base import UsageTeamStatus


class TenkoThunderbolts(UsageTeamStatus):
    name: Literal['Tenko Thunderbolts'] = 'Tenko Thunderbolts'
    desc: str = '''Before you choose your action: Deal 3 Electro DMG.'''
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Attack opponent active charactor
        """
        if self.position.player_idx != event.player_idx:
            # not our turn
            return []
        target_table = match.player_tables[1 - self.position.player_idx]
        target_charactor_idx = target_table.active_charactor_idx
        target_charactor = target_table.charactors[target_charactor_idx]
        self.usage -= 1
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target_charactor.position,
                    damage = 3,
                    damage_elemental_type = DamageElementalType.ELECTRO,
                    cost = Cost()
                )
            ],
        )]


ElectroTeamStatus = TenkoThunderbolts | TenkoThunderbolts
