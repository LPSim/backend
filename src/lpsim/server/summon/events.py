from typing import Literal

from ..consts import DamageElementalType
from .base import AttackerSummonBase


class CryoHilichurlShooter(AttackerSummonBase):
    name: Literal['Cryo Hilichurl Shooter'] = 'Cryo Hilichurl Shooter'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1


class ElectroHilichurlShooter(AttackerSummonBase):
    name: Literal['Electro Hilichurl Shooter'] = 'Electro Hilichurl Shooter'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1


class HilichurlBerserker(AttackerSummonBase):
    name: Literal['Hilichurl Berserker'] = 'Hilichurl Berserker'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 1


class HydroSamachurl(AttackerSummonBase):
    name: Literal['Hydro Samachurl'] = 'Hydro Samachurl'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1


EventSummons = (
    CryoHilichurlShooter | ElectroHilichurlShooter | HilichurlBerserker
    | HydroSamachurl
)
