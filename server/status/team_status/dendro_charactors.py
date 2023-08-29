

from typing import List, Literal

from server.action import ChangeObjectUsageAction
from server.event import CreateObjectEventArguments

from ...consts import ElementType, ElementalReactionType, ObjectPositionType

from ...modifiable_values import DamageIncreaseValue
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
        self, event: CreateObjectEventArguments
    ) -> List[ChangeObjectUsageAction]:
        """
        When self is created, check whether to increase the usage of Seed of
        Skandha.
        """
        if event.action.object_name != 'Shrine of Maya':
            # not creating Shrine of Maya, do nothing.
            return []
        match = event.match
        active_charactor = match.player_tables[
            self.position.player_id].get_active_charactor()
        assert active_charactor is not None
        if (
            active_charactor.name == 'Nahida' 
            and active_charactor.talent is not None
        ):
            # talent equipped, check if have electro charactor.
            has_electro_charactor = False
            for charactor in match.player_tables[
                    self.position.player_id].charactors:
                if charactor.element == ElementType.ELECTRO:
                    has_electro_charactor = True
                    break
            if has_electro_charactor:
                # has electro charactor, add one usage for enemy
                # Seed of Skandha.
                ret = []
                for charactor in match.player_tables[
                        1 - self.position.player_id].charactors:
                    for status in charactor.status:
                        if status.name == 'Seed of Skandha':
                            position = status.position.copy(deep = True)
                            position.area = \
                                ObjectPositionType.CHARACTOR_STATUS
                            ret.append(
                                ChangeObjectUsageAction(
                                    object_position = position,
                                    object_id = status.id,
                                    change_usage = 1,
                                    change_type = 'DELTA',
                                )
                            )
                return ret
        return []

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        +1 on self elemental reaction damage.
        """
        if value.target_position.player_id == self.position.player_id:
            # attack self, not activate
            return value
        if value.position.player_id != self.position.player_id:
            # not self, not activate
            return value
        if value.element_reaction is not ElementalReactionType.NONE:
            value.damage += 1
        return value


DendroTeamStatus = ShrineOfMaya | ShrineOfMaya
