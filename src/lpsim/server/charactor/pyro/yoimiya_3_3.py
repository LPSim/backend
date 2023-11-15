from typing import List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import SkillTalent
from ...consts import DieColor
from ...struct import Cost
from .yoimiya_3_8 import Yoimiya_3_8 as Y_3_8
from .yoimiya_3_8 import RyuukinSaxifrage as RS_3_8
from .yoimiya_3_8 import FireworkFlareUp, NiwabiFireDance


class RyuukinSaxifrage(RS_3_8):
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )


class NaganoharaMeteorSwarm_3_3(SkillTalent):
    name: Literal['Naganohara Meteor Swarm']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Yoimiya'] = 'Yoimiya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2,
    )
    skill: Literal['Niwabi Fire-Dance'] = 'Niwabi Fire-Dance'
    status_max_usage: int = 2


class Yoimiya_3_3(Y_3_8):
    version: Literal['3.3']
    max_charge: int = 2
    skills: List[FireworkFlareUp | NiwabiFireDance | RyuukinSaxifrage] = []

    def _init_skills(self) -> None:
        self.skills = [
            FireworkFlareUp(),
            NiwabiFireDance(),
            RyuukinSaxifrage()
        ]


register_class(Yoimiya_3_3 | NaganoharaMeteorSwarm_3_3)
