from typing import Literal
from .base import ShieldCharactorStatus


class LithicSpear(ShieldCharactorStatus):
    name: Literal['Lithic Spear'] = 'Lithic Spear'
    desc: str = (
        'Grants XXX Shield point to defend your active charactor. '
    )
    version: Literal['3.3'] = '3.3'
    usage: int
    max_usage: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.desc = self.desc.replace('XXX', str(self.usage))

    def renew(self, object: 'LithicSpear') -> None:
        self.max_usage = object.max_usage
        self.usage = max(object.usage, self.usage)
        self.usage = min(self.max_usage, self.usage)
        self.desc = object.desc


WeaponCharactorStatus = LithicSpear | LithicSpear
