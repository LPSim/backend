from typing import Any, List, Literal

from ...consts import ELEMENT_TO_DIE_COLOR

from ...action import (
    ActionTypes, ChargeAction, CreateDiceAction, CreateObjectAction, 
    RemoveObjectAction
)
from ...struct import Cost, ObjectPosition
from .others import IHaventLostYet as IHLY_4_0
from .others import SendOff as SendOff_3_7
from .foods import MintyMeatRolls as MintyMeatRolls_3_4
from .resonance import ThunderAndEternity as TAE_4_0


class ThunderAndEternity_3_7(TAE_4_0):
    name: Literal['Thunder and Eternity']
    desc: str = (
        'Convert all your Elemental Dice to the Type of the active character. '
        '(You must have at least 2 Inazuman characters in your deck to add '
        'this card to your deck.)'
    )
    version: Literal['3.7']

    def get_dice_color(self, match: Any) -> str:
        """
        Convert all your Elemental Dice to the Type of the active character.
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return ELEMENT_TO_DIE_COLOR[charactor.element]


class IHaventLostYet_3_3(IHLY_4_0):
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


class SendOff_3_3(SendOff_3_7):
    name: Literal['Send Off']
    desc: str = '''Choose one Summon on the opposing side and destroy it.'''
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[RemoveObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is not None
        return [RemoveObjectAction(
            object_position = target,
        )]


class MintyMeatRolls_3_3(MintyMeatRolls_3_4):
    version: Literal['3.3']
    desc: str = (
        "Before this Round ends, the target character's Normal Attacks cost 1 "
        "less Unaligned Element."
    )


OldVersionEventCards = (
    ThunderAndEternity_3_7 | IHaventLostYet_3_3 | SendOff_3_3 
    | MintyMeatRolls_3_3
)
