from typing import Any, List, Literal

from ..charactor_base import PhysicalNormalAttackBase

from ...action import ActionTypes, Actions

from ..anemo.maguu_kenki import MaguuKenki as MK_3_4
from ..anemo.maguu_kenki import BlusteringBlade as BB_3_4
from ..anemo.maguu_kenki import FrostyAssault as FA_3_4
from ..anemo.maguu_kenki import PseudoTenguSweeper


class BlusteringBlade(BB_3_4):
    desc: str = '''Deals 1 Anemo DMG, summons 1 Shadowsword: Lone Gale.'''
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
    desc: str = '''Deals 1 Anemo DMG, summons 1 Shadowsword: Lone Gale.'''
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
