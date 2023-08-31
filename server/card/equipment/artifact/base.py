from typing import Literal, List, Any

from ....event import MoveObjectEventArguments

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
    type: Literal[ObjectType.ARTIFACT] = ObjectType.ARTIFACT
    cost_label: int = CostLabels.CARD.value | CostLabels.ARTIFACT.value

    version: str
    cost: Cost
    usage: int

    def equip(self, match: Any) -> list[Actions]:
        """
        The artifact is equipped, i.e. from hand to charactor. Set the status
        of artifact, and if it has actions when equipped, return the actions.
        """
        # should be used by small qianyan
        raise NotImplementedError('Not tested part')
        return []

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # can quip on all self alive charactors
        ret: List[ObjectPosition] = []
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if charactor.is_alive:
                ret.append(charactor.position)
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
        charactor_id = target.id
        assert position.area == ObjectPositionType.CHARACTOR
        assert position.player_idx == self.position.player_idx
        charactors = match.player_tables[position.player_idx].charactors
        for charactor in charactors:
            if charactor.id == charactor_id:
                # check if need to remove current artifact
                if charactor.artifact is not None:
                    ret.append(RemoveObjectAction(
                        object_position = charactor.artifact.position,
                    ))
        ret.append(MoveObjectAction(
            object_position = self.position,
            target_position = position,
        ))
        return ret

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> list[Actions]:
        """
        When this artifact is moved from hand to charactor, it is considered
        as equipped, and will call `self.equip`.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.HAND
            and event.action.target_position.area 
            == ObjectPositionType.CHARACTOR
        ):
            # this artifact equipped from hand to charactor
            return self.equip(match)
        return []
