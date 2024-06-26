from typing import Any, Literal

from .....utils.class_registry import register_class

from .base import RoundEffectArtifactBase
from ....struct import Cost
from ....modifiable_values import CostValue, InitialDiceColorValue
from ....consts import ELEMENT_TO_DIE_COLOR, ElementType, ObjectPositionType


class SmallElementalArtifact_4_0(RoundEffectArtifactBase):
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
    cost: Cost = Cost(any_dice_number=2)
    element: ElementType = ElementType.NONE
    max_usage_per_round: int = 1

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
        else:
            assert self.name == "Witch's Scorching Hat", "Unknown name"
            self.element = ElementType.PYRO

    def value_modifier_COST(
        self,
        value: CostValue,
        match: Any,
        mode: Literal["TEST", "REAL"],
    ) -> CostValue:
        """
        When character equipped with this artifact and used skill, decrease
        the elemental cost by 1. If element not match, decrease any dice cost
        by 1.
        """
        if self.usage > 0:
            # has usage
            if not self._check_value_self_skill_or_talent(value, match):
                return value
            # can decrease cost
            if value.cost.decrease_cost(ELEMENT_TO_DIE_COLOR[self.element]):
                # decrease cost success
                if mode == "REAL":
                    self.usage -= 1
        return value


class BigElementalArtifact_4_0(SmallElementalArtifact_4_0):
    """
    Seven artifacts that decrease elemental cost and fix colors of two dice.
    """

    name: Literal[
        "Blizzard Strayer",  # cryo
        "Deepwood Memories",  # dendro
        "Archaic Petra",  # geo
        "Thundering Fury",  # electro
        "Viridescent Venerer",  # anemo
        "Heart of Depth",  # hydro
        "Crimson Witch of Flames",  # pyro
    ]
    version: Literal["4.0"] = "4.0"
    usage: int = 1
    cost: Cost = Cost(same_dice_number=2)
    element: ElementType = ElementType.NONE
    max_usage_per_round: int = 1

    def __init__(self, *argv, **kwargs):
        super(SmallElementalArtifact_4_0, self).__init__(*argv, **kwargs)
        if self.name == "Blizzard Strayer":
            self.element = ElementType.CRYO
        elif self.name == "Deepwood Memories":
            self.element = ElementType.DENDRO
        elif self.name == "Archaic Petra":
            self.element = ElementType.GEO
        elif self.name == "Thundering Fury":
            self.element = ElementType.ELECTRO
        elif self.name == "Viridescent Venerer":
            self.element = ElementType.ANEMO
        elif self.name == "Heart of Depth":
            self.element = ElementType.HYDRO
        else:
            assert self.name == "Crimson Witch of Flames", "Unknown name"
            self.element = ElementType.PYRO

    def value_modifier_INITIAL_DICE_COLOR(
        self, value: InitialDiceColorValue, match: Any, mode: Literal["REAL", "TEST"]
    ) -> InitialDiceColorValue:
        """
        If self equipped with this artifact, fix two dice colors to self
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not in character area, do nothing
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        value.dice_colors += [ELEMENT_TO_DIE_COLOR[self.element]] * 2
        return value


class SmallElementalArtifact_3_3(SmallElementalArtifact_4_0):
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(same_dice_number=2)


class BigElementalArtifact_3_6(BigElementalArtifact_4_0):
    version: Literal["3.6"] = "3.6"
    cost: Cost = Cost(any_dice_number=3)


class BigElementalArtifact_3_3(BigElementalArtifact_4_0):
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(same_dice_number=3)


register_class(
    SmallElementalArtifact_4_0
    | BigElementalArtifact_4_0
    | BigElementalArtifact_3_6
    | BigElementalArtifact_3_3
    | SmallElementalArtifact_3_3
)
