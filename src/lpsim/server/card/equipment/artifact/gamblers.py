from typing import Any, List, Literal

from .base import ArtifactBase

from ....consts import DieColor, ObjectPositionType

from ....struct import Cost, ObjectPosition

from ....event import CharactorDefeatedEventArguments
from ....action import CreateDiceAction, Actions


class GamblersEarrings(ArtifactBase):
    name: Literal["Gambler's Earrings"]
    desc: str = (
        'After an opposing character is defeated: If the character this card '
        'is attached to is the active character, create Omni Element x2. '
        '(Can happen 3 times per match)'
    )
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 3

    def equip(self, match: Any) -> List[Actions]:
        """
        Equip this artifact. Reset usage.
        """
        self.usage = 3
        return []

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When an opposing character is defeated, check if the character this 
        card is attached to is the active character. If so, create Omni 
        Element x2.
        """
        target_position = ObjectPosition(
            player_idx = event.action.player_idx,
            # all the following are not used to check, no need to set correctly
            area = ObjectPositionType.INVALID,
            id = -1,
        )
        if not self.position.check_position_valid(
            target_position, match, 
            player_idx_same = False,
            source_area = ObjectPositionType.CHARACTOR,
            source_is_active_charactor = True,
        ):
            # our charactor defeated, or self not active, or self not equipped
            return []
        if self.usage <= 0:
            # no usage left
            return []
        self.usage -= 1
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 2,
            color = DieColor.OMNI
        )]


Gamblers = GamblersEarrings | GamblersEarrings
