from typing import Any, List, Literal

from ....consts import FactionType

from ....action import Actions

from .other_polearm import LithicSpear as LS_3_7


class LithicSpear_3_3(LS_3_7):
    desc: str = (
        'The character deals +1 DMG. '
        'When played: For each alive party member from Liyue, grant 1 Shield '
        'point to the character to which this is attached. (Max 3 points)'
    )
    version: Literal['3.3']

    def equip(self, match: Any) -> List[Actions]:
        """
        Generate shield
        """
        count = 0
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.is_alive and FactionType.LIYUE in c.faction:
                count += 1
        return self.generate_shield(count)


OldVersionWeapons = LithicSpear_3_3 | LithicSpear_3_3
