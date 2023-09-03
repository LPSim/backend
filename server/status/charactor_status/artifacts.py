from typing import Literal
from .base import ShieldCharactorStatus


class UnmovableMountain(ShieldCharactorStatus):
    name: Literal['Unmovable Mountain'] = 'Unmovable Mountain'
    desc: str = '''Provides 2 Shield to protect the equipped charactor.'''
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2


ArtifactCharactorStatus = UnmovableMountain | UnmovableMountain
