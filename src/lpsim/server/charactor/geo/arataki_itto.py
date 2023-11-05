from typing import List, Literal
from ..old_version.arataki_itto_3_6 import (
    AratakiItto_3_6,  FightClubLegend, MasatsuZetsugiAkaushiBurst,
    RoyalDescentBeholdIttoTheEvil as RDBITE_3_6
)


class RoyalDescentBeholdIttoTheEvil(RDBITE_3_6):
    damage: int = 4
    version: Literal['4.2'] = '4.2'


class AratakiItto(AratakiItto_3_6):
    version: Literal['4.2'] = '4.2'
    skills: List[
        FightClubLegend | MasatsuZetsugiAkaushiBurst 
        | RoyalDescentBeholdIttoTheEvil
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            FightClubLegend(),
            MasatsuZetsugiAkaushiBurst(),
            RoyalDescentBeholdIttoTheEvil(),
        ]
