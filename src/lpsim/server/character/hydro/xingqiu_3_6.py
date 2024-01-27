from typing import List, Literal

from ....utils.class_registry import register_class

from .xingqiu_4_1 import Xingqiu_4_1 as X_4_1
from .xingqiu_4_1 import Raincutter as R_4_1
from .xingqiu_4_1 import GuhuaStyle, FatalRainscreen


class Raincutter(R_4_1):
    name: Literal['Raincutter'] = 'Raincutter'
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


register_class(Xingqiu_3_6)
