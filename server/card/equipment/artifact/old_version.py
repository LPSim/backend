from typing import Literal

from ....struct import Cost
from .element_artifacts import SmallElementalArtifact as SEA_4_0


class SmallElementalArtifact(SEA_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 2)


OldVersionArtifacts = SmallElementalArtifact | SmallElementalArtifact
