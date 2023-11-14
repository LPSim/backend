from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions
from ...consts import DamageElementalType
from .xingqiu_3_6 import Xingqiu_3_6 as X_3_6
from .xingqiu_3_6 import Raincutter as R_3_6
from .xingqiu_4_1 import GuhuaStyle, FatalRainscreen


class Raincutter(R_3_6):
    name: Literal['Raincutter'] = 'Raincutter'

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, application and create version 3.3 object
        """
        ret = [
            self.charge_self(-2),
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.element_application_self(match, DamageElementalType.HYDRO)
        ]
        return ret + [
            self.create_team_status('Rainbow Bladework', {
                'version': '3.3'
            })
        ]


class Xingqiu_3_3(X_3_6):
    version: Literal['3.3']
    skills: List[GuhuaStyle | FatalRainscreen | Raincutter] = []

    def _init_skills(self) -> None:
        self.skills = [
            GuhuaStyle(),
            FatalRainscreen(),
            Raincutter()
        ]


register_class(Xingqiu_3_3)
