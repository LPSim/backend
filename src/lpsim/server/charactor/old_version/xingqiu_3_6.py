from typing import List, Literal

from ..hydro.xingqiu import Xingqiu as X_4_1
from ..hydro.xingqiu import Raincutter as R_4_1
from ..hydro.xingqiu import GuhuaStyle, FatalRainscreen


class Raincutter(R_4_1):
    name: Literal['Raincutter'] = 'Raincutter'
    desc: str = (
        'Deals 1 Hydro DMG, grants this character Hydro Application, creates '
        '1 Rainbow Bladework.'
    )
    damage: int = 1


class Xingqiu_3_6(X_4_1):
    version: Literal['3.6']
    skills: List[GuhuaStyle | FatalRainscreen | Raincutter] = []

    def _init_skills(self) -> None:
        self.skills = [
            GuhuaStyle(),
            FatalRainscreen(),
            Raincutter()
        ]
