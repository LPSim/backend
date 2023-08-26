from typing import Literal, List, Any

from ....object_base import CardBase
from ....struct import DiceCost
from ....consts import ObjectType, DiceCostLabels, ObjectPositionType
from ....action import MoveObjectAction, RemoveObjectAction
from ....struct import CardActionTarget


class ArtifactBase(CardBase):
    """
    Base class of artifacts.
    """
    name: str
    type: Literal[ObjectType.ARTIFACT] = ObjectType.ARTIFACT
    cost_label: int = DiceCostLabels.CARD.value | DiceCostLabels.ARTIFACT.value

    version: str
    cost: DiceCost
    usage: int

    def act(self):
        """
        when this support card is activated from hand, this function is called
        to update the status.
        """
        raise NotImplementedError()

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        # can quip on all self alive charactors
        ret: List[CardActionTarget] = []
        for charactor in match.player_tables[
                self.position.player_id].charactors:
            if charactor.is_alive:
                ret.append(CardActionTarget(
                    target_position = charactor.position.copy(deep = True),
                    target_id = charactor.id,
                ))
        return ret

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[MoveObjectAction | RemoveObjectAction]:
        """
        Act the artifact. will place it into artifact area.
        When artifact is equipped, remove the old one.
        """
        assert target is not None
        ret: List[MoveObjectAction | RemoveObjectAction] = []
        position = target.target_position
        id = target.target_id
        assert position.area == ObjectPositionType.CHARACTOR
        assert position.player_id == self.position.player_id
        charactors = match.player_tables[position.player_id].charactors
        for charactor in charactors:
            if charactor.id == id:
                # check if need to remove current artifact
                if charactor.artifact is not None:
                    ret.append(RemoveObjectAction(
                        object_position = charactor.artifact.position,
                        object_id = charactor.artifact.id,
                    ))
        ret.append(MoveObjectAction(
            object_position = self.position,
            object_id = self.id,
            target_position = position.copy(deep = True),
        ))
        return ret
