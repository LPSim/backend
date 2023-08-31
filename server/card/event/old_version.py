from typing import Any, List, Literal

from ...action import (
    ActionTypes, ChargeAction, CreateDiceAction, CreateObjectAction
)
from ...struct import Cost, ObjectPosition
from .others import IHaventLostYet as IHLY_4_0


class IHaventLostYet(IHLY_4_0):
    name: Literal["I Haven't Lost Yet!"]
    desc: str = (
        "Only playable if one of your characters is defeated this Round: "
        "Create Omni Element x1 and your current active character gains 1 "
        "Energy. "
    )
    version: Literal['3.3']
    cost: Cost = Cost()

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction | CreateDiceAction | CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert ret[-1].type == ActionTypes.CREATE_OBJECT
        # old version not adding team status
        ret = ret[:-1]
        return ret


OldVersionEventCards = IHaventLostYet | IHaventLostYet
