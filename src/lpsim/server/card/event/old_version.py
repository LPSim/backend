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
from .others import MasterOfWeaponry as MOW_4_1
from .others import BlessingOfTheDivineRelicsInstallation as BOTDRI_4_1
from .resonance import WindAndFreedom as WAF_4_1
from .foods import TeyvatFriedEgg as TFE_4_1


class ThunderAndEternity_3_7(TAE_4_0):
    name: Literal['Thunder and Eternity']
    desc: str = (
        'Convert all your Elemental Dice to the Type of the active character. '
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


class MasterOfWeaponry_3_3(MOW_4_1):
    desc: str = (
        'Shift 1 Weapon Equipment Card that has been equipped to one of your '
        'characters to another one of your characters of the same Weapon '
        'Type.'
    )
    version: Literal['3.3']
    reset_usage: bool = False


class BlessingOfTheDivineRelicsInstallation_3_3(BOTDRI_4_1):
    desc: str = (
        'Shift 1 Artifact Equipment Card that has been equipped to one of '
        'your characters to another one of your characters. '
    )
    version: Literal['3.3']
    reset_usage: bool = False


class WindAndFreedom_3_7(WAF_4_1):
    name: Literal['Wind and Freedom']
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends. '
    )
    version: Literal['3.7']


class TeyvatFriedEgg_3_7(TFE_4_1):
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 3)


OldVersionEventCards = (
    WindAndFreedom_3_7 | ThunderAndEternity_3_7 | TeyvatFriedEgg_3_7

    | IHaventLostYet_3_3 | MasterOfWeaponry_3_3 
    | BlessingOfTheDivineRelicsInstallation_3_3 | SendOff_3_3 
    | MintyMeatRolls_3_3
)
