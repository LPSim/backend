from typing import Any, Literal

from ...consts import DamageElementalType

from ...modifiable_values import DamageIncreaseValue
from .base import ElementalInfusionCharactorStatus, RoundCharactorStatus


class ElectroInfusionKeqing(ElementalInfusionCharactorStatus,
                            RoundCharactorStatus):
    """
    Inherit from vanilla elemental infusion status, and has talent activated
    argument. when talent activated, it will gain electro damage +1 buff,
    and usage +1.
    """
    name: Literal['Electro Elemental Infusion'] = 'Electro Elemental Infusion'
    mark: Literal['Keqing']  # used to select right status
    buff_desc: str = (
        'When the charactor to which it is attached to deals '
        'Physical Damage, it will be turned into XXX DMG, '
        'and Electro DMG dealt by the charactor +1.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2

    talent_activated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = self.buff_desc

    def renew(self, new_status: 'ElectroInfusionKeqing') -> None:
        if self.max_usage < new_status.max_usage:
            self.max_usage = new_status.max_usage
        if self.usage < new_status.usage:
            self.usage = new_status.usage
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = self.buff_desc

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If talent activated, increase electro damage dealt by this charactor 
        by 1.
        """
        if not self.talent_activated:
            # talent not activated, do nothing
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use skill, do nothing
            return value
        if value.damage_elemental_type != DamageElementalType.ELECTRO:
            # not electro damage, do nothing
            return value
        value.damage += 1
        return value


ElectroCharactorStatus = ElectroInfusionKeqing | ElectroInfusionKeqing
