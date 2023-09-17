from typing import Literal
from .base import ShieldTeamStatus


class RebelliousShield(ShieldTeamStatus):
    name: Literal['Rebellious Shield'] = 'Rebellious Shield'
    desc: str = (
        'Grants 1 Shield point to defend your active charactor. '
        '(Can stack. Max 2 Points.)'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 2


WeaponTeamStatus = RebelliousShield | RebelliousShield
