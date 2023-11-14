from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase

from ...action import ActionTypes, Actions

from .maguu_kenki_3_4 import MaguuKenki_3_4 as MK_3_4
from .maguu_kenki_3_4 import BlusteringBlade as BB_3_4
from .maguu_kenki_3_4 import FrostyAssault as FA_3_4
from .maguu_kenki_3_4 import PseudoTenguSweeper


class BlusteringBlade(BB_3_4):
    damage: int = 1

    def get_actions(self, match: Any) -> List[Actions]:
        """
        gather two actions
        """
        actions = super().get_actions(match)
        attack_actions = super(BB_3_4, self).get_actions(match)
        assert len(actions) == 2
        summon_action = actions[0]
        assert summon_action.type == ActionTypes.CREATE_OBJECT
        attack_actions.append(summon_action)
        return attack_actions


class FrostyAssault(FA_3_4):
    damage: int = 1

    def get_actions(self, match: Any) -> List[Actions]:
        """
        gather two actions
        """
        actions = super().get_actions(match)
        attack_actions = super(FA_3_4, self).get_actions(match)
        assert len(actions) == 2
        summon_action = actions[0]
        assert summon_action.type == ActionTypes.CREATE_OBJECT
        attack_actions.append(summon_action)
        return attack_actions


class MaguuKenki_3_3(MK_3_4):
    version: Literal['3.3']
    skills: List[
        PhysicalNormalAttackBase
        | BlusteringBlade | FrostyAssault | PseudoTenguSweeper
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Ichimonji',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            BlusteringBlade(),
            FrostyAssault(),
            PseudoTenguSweeper()
        ]


register_class(MaguuKenki_3_3)
