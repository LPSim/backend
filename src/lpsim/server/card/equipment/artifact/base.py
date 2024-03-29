from typing import Literal, List, Any

from .....utils.class_registry import register_base_class

from ....event import MoveObjectEventArguments, RoundPrepareEventArguments

from ....object_base import CardBase
from ....struct import Cost
from ....consts import ObjectType, CostLabels, ObjectPositionType
from ....action import Actions, MoveObjectAction, RemoveObjectAction
from ....struct import ObjectPosition


class ArtifactBase(CardBase):
    """
    Base class of artifacts.
    """

    name: str
    version: str
    cost: Cost
    usage: int

    type: Literal[ObjectType.ARTIFACT] = ObjectType.ARTIFACT
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.ARTIFACT.value | CostLabels.EQUIPMENT.value
    )
    remove_when_used: bool = False

    def equip(self, match: Any) -> List[Actions]:
        """
        The artifact is equipped, i.e. from hand to character. Set the status
        of artifact, and if it has actions when equipped, return the actions.
        """
        # should be used by small qianyan
        return []

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # can quip on all self alive characters
        ret: List[ObjectPosition] = []
        for character in match.player_tables[self.position.player_idx].characters:
            if character.is_alive:
                ret.append(character.position)
        return ret

    def is_valid(self, match: Any) -> bool:
        # can only be used when in hand
        return self.position.area == ObjectPositionType.HAND

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MoveObjectAction | RemoveObjectAction]:
        """
        Act the artifact. will place it into artifact area.
        When other artifact is equipped, remove the old one.
        """
        assert target is not None
        ret: List[MoveObjectAction | RemoveObjectAction] = []
        position = target.set_id(self.id)
        character_id = target.id
        assert position.area == ObjectPositionType.CHARACTER
        assert position.player_idx == self.position.player_idx
        characters = match.player_tables[position.player_idx].characters
        for character in characters:
            if character.id == character_id:
                # check if need to remove current artifact
                if character.artifact is not None:
                    ret.append(
                        RemoveObjectAction(
                            object_position=character.artifact.position,
                        )
                    )
        ret.append(
            MoveObjectAction(
                object_position=self.position,
                target_position=position,
            )
        )
        return ret

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When this artifact is moved from hand to character, it is considered
        as equipped, and will call `self.equip`.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.HAND
            and event.action.target_position.area == ObjectPositionType.CHARACTER
        ):
            # this artifact equipped from hand to character
            return self.equip(match)
        return []


register_base_class(ArtifactBase)


class RoundEffectArtifactBase(ArtifactBase):
    """
    Artifacts that has round effects. Refresh their usage when equipped and
    at round preparing stage.
    Instead of setting usage, set max_usage_per_round.
    """

    name: str
    version: str
    cost: Cost
    max_usage_per_round: int

    usage: int = 0

    def equip(self, match: Any) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When this weapon is moved from character to character, and mark as
        reset_usage, reset usage.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.CHARACTER
            and event.action.target_position.area == ObjectPositionType.CHARACTER
            and event.action.reset_usage
        ):
            # this weapon equipped from character to character
            self.usage = self.max_usage_per_round
        return super().event_handler_MOVE_OBJECT(event, match)
