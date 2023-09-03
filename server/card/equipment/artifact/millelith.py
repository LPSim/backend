from typing import Any, List, Literal

from ....consts import ELEMENT_TO_DIE_COLOR, ObjectPositionType

from ....action import CreateDiceAction, CreateObjectAction

from ....event import ReceiveDamageEventArguments, RoundPrepareEventArguments

from ....struct import Cost
from .base import ArtifactBase, RoundEffectArtifactBase


class GeneralsAncientHelm(ArtifactBase):
    name: Literal["General's Ancient Helm"]
    desc: str = (
        'When Action Phase begins: The character to which this is attached '
        'gains Unmovable Mountain that provides 2 Shield points.'
    )
    version: Literal['3.5'] = '3.5'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create Unmovable Mountain for this charactor.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        position = self.position.set_area(ObjectPositionType.CHARACTOR_STATUS)
        return [CreateObjectAction(
            object_name = 'Unmovable Mountain',
            object_position = position,
            object_arguments = {}
        )]


class TenacityOfTheMillelith(RoundEffectArtifactBase):
    name: Literal['Tenacity of the Millelith']
    desc: str = (
        'When Action Phase begins: The character to which this is attached '
        'gains Unmovable Mountain that provides 2 Shield points. '
        'After this character takes DMG: If the character this card is '
        'attached to is the active character, create 1 Elemental Die matching '
        "this character's Elemental Type. (Once per Round) "
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 3)
    max_usage_per_round: int = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        super().event_handler_ROUND_PREPARE(event, match)
        position = self.position.set_area(ObjectPositionType.CHARACTOR_STATUS)
        return [CreateObjectAction(
            object_name = 'Unmovable Mountain',
            object_position = position,
            object_arguments = {}
        )]

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When this charactor received damage and is active charactor, create
        elemental die.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        if self.usage == 0:
            # no usage
            return []
        damage = event.final_damage
        if not self.position.check_position_valid(
            damage.target_position, match, player_idx_same = True,
            charactor_idx_same = True, source_is_active_charactor = True
        ):
            # damage not attack self, or self not active charactor
            return []
        # create die
        self.usage -= 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx
        ]
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 1,
            color = ELEMENT_TO_DIE_COLOR[charactor.element]
        )]


MillelithArtifacts = GeneralsAncientHelm | TenacityOfTheMillelith
