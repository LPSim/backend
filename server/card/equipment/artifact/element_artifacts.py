from typing import Any, Literal

from server.action import Actions

from .base import ArtifactBase
from ....struct import Cost
from ....modifiable_values import CostValue
from ....consts import ElementType, ObjectPositionType, CostLabels
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

    desc: str = (
        'When the character uses a Skill or equips a Talent: Spend 1 less'
        'XXX Die. (Once per Round)'
    )
    version: Literal["4.0"] = "4.0"
    usage: int = 1
    cost: Cost = Cost(any_dice_number = 2)
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
        else:
            assert self.name == "Witch's Scorching Hat"
            self.element = ElementType.PYRO
        self.desc = self.desc.replace(
            "XXX", self.element.value.capitalize()
        )

    def equip(self, match: Any) -> list[Actions]:
        """
        Equip this artifact. Reset usage.
        """
        self.usage = 1
        return []

    def event_handler_ROUND_PREPARE(self, event: RoundPrepareEventArguments) \
            -> list[ActionBase]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def value_modifier_COST(
        self, 
        value: CostValue, 
        mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        When charactor equipped with this artifact and used skill, decrease
        the elemental cost by 1. If element not match, decrease any dice cost
        by 1.
        """
        if self.usage > 0:  
            # has usage
            if not self.position.check_position_valid(
                value.position, value.match,
                player_idx_same = True, 
                source_area = ObjectPositionType.CHARACTOR,
            ):
                # not from self position or not equipped
                return value
            label = value.cost.label
            if label & (
                CostLabels.NORMAL_ATTACK.value
                | CostLabels.ELEMENTAL_SKILL.value
                | CostLabels.ELEMENTAL_BURST.value
                | CostLabels.TALENT.value
            ) == 0:  # no label match
                return value
            position = value.position
            assert self.position.charactor_idx != -1
            if position.area == ObjectPositionType.CHARACTOR:
                # cost from charactor
                if position.charactor_idx != self.position.charactor_idx:
                    # not same charactor
                    return value
            else:
                assert position.area == ObjectPositionType.HAND
                # cost from hand card, is a talent card
                equipped_charactor = value.match.player_tables[
                    self.position.player_idx
                ].charactors[self.position.charactor_idx]
                for card in value.match.player_tables[
                        self.position.player_idx].hands:
                    if card.id == value.position.id:
                        if card.charactor_name != equipped_charactor.name:
                            # talent card not for this charactor
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


ElementArtifacts = SmallElementalArtifact | SmallElementalArtifact
