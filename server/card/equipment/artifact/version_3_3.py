from typing import Literal
from .base import ArtifactBase
from ....struct import DiceCost
from ....modifiable_values import DiceCostValue
from ....consts import ElementType, ObjectPositionType, DiceCostLabels
from ....event import RoundPrepareEventArguments
from ....action import ActionBase


class SmallElementalArtifact(ArtifactBase):
    """
    Seven artifacts that decrease elemental cost.
    """

    name: Literal[
        "Broken Rime's Echo",  # cryo
        "Laurel Coronet",  # dendro
        "Mask of Solitude Basalt",  # geo
        "Thunder Summoner's Crown",  # electro
        "Viridescent Venerer's Diadem",  # anemo
        "Wine-Stained Tricorne",  # hydro
        "Witch's Scorching Hat",  # pyro
    ]

    version: Literal["4.0"] = "4.0"
    usage: int = 1
    cost: DiceCost = DiceCost(any_dice_number=2)
    element: ElementType = ElementType.NONE

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Broken Rime's Echo":
            self.element = ElementType.CRYO
        elif self.name == "Laurel Coronet":
            self.element = ElementType.DENDRO
        elif self.name == "Mask of Solitude Basalt":
            self.element = ElementType.GEO
        elif self.name == "Thunder Summoner's Crown":
            self.element = ElementType.ELECTRO
        elif self.name == "Viridescent Venerer's Diadem":
            self.element = ElementType.ANEMO
        elif self.name == "Wine-Stained Tricorne":
            self.element = ElementType.HYDRO
        elif self.name == "Witch's Scorching Hat":
            self.element = ElementType.PYRO

    def event_handler_ROUND_PREPARE(self, event: RoundPrepareEventArguments) \
            -> list[ActionBase]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def act(self):
        """
        When activated, reset usage
        """
        self.usage = 1

    def value_modifier_DICE_COST(
        self, 
        value: DiceCostValue, 
        mode: Literal['TEST', 'REAL'],
    ) -> DiceCostValue:
        """
        When charactor equipped with this artifact and used skill, decrease
        the elemental cost by 1. If element not match, decrease any dice cost
        by 1.
        """
        if (
            self.usage > 0 
            and self.position.area == ObjectPositionType.CHARACTOR
        ):  # has usage and equipped
            label = value.cost.label
            if label & (
                DiceCostLabels.NORMAL_ATTACK.value
                | DiceCostLabels.ELEMENTAL_SKILL.value
                | DiceCostLabels.ELEMENTAL_BURST.value
            ) == 0:  # no label match
                return value
            position = value.position
            if position.area != ObjectPositionType.CHARACTOR:
                # cost not from charactor
                return value
            assert self.position.charactor_id != -1
            if position.charactor_id != self.position.charactor_id:
                # not same charactor
                return value
            # can decrease cost
            used = 0
            if (value.cost.elemental_dice_color == self.element
                    and value.cost.elemental_dice_number > 0):
                value.cost.elemental_dice_number -= 1
                used += 1
            elif value.cost.any_dice_number > 0:
                value.cost.any_dice_number -= 1
                used += 1
            if mode == 'REAL':
                self.usage -= used
        return value
