from typing import Any, List, Literal

from ...action import Actions
from ...consts import DamageElementalType
from ..hydro.xingqiu import Xingqiu as X_3_6
from ..hydro.xingqiu import Raincutter as R_3_6
from ..hydro.xingqiu import GuhuaStyle, FatalRainscreen


class Raincutter(R_3_6):
    name: Literal['Raincutter'] = 'Raincutter'
    desc: str = (
        'Deals 1 Hydro DMG, grants this character Hydro Application, creates '
        '1 Rainbow Bladework (version 3.3).'
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, application and create version 3.3 object
        """
        ret = super(R_3_6, self).get_actions(match)
        ret += [
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
