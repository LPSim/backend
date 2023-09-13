
from typing import Any, Literal

from ...consts import DamageElementalType, SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import (
    ElementalInfusionCharactorStatus, RoundCharactorStatus, 
    UsageCharactorStatus
)


class Grimheart(UsageCharactorStatus):
    name: Literal['Grimheart'] = 'Grimheart'
    desc: str = (
        'After the character to which this is attached uses Icetide Vortex: '
        'Remove this status, DMG +_DAMAGE_ for this instance.'
    )
    version: Literal['3.8'] = '3.8'
    damage: int = 3
    usage: int = 1
    max_usage: int = 1

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.version == '3.5':
            self.damage = 2
        else:
            assert self.version == '3.8'
            self.damage = 3
        self.desc = self.desc.replace('_DAMAGE_', str(self.damage))

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        When character uses Icetide Vortex, increase damage by self.damage
        """
        if value.damage_from_element_reaction:
            # from element reaction, do nothing
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_SKILL
        ):
            # not self use elemental skill, do nothing
            return value
        assert self.usage > 0
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += self.damage
        return value


class CryoFusionAyaka(ElementalInfusionCharactorStatus,
                      RoundCharactorStatus):
    """
    Inherit from vanilla elemental infusion status, and has talent activated
    argument. when talent activated, it will gain electro damage +1 buff,
    and usage +1.
    """
    name: Literal['Cryo Elemental Infusion'] = 'Cryo Elemental Infusion'
    mark: Literal['Kamisato Ayaka']  # used to select right status
    buff_desc: str = (
        'When the charactor to which it is attached to deals '
        'Physical Damage, it will be turned into Cryo DMG, '
        'and Cryo DMG dealt by the charactor +1.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    talent_activated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = self.buff_desc

    def renew(self, new_status: 'CryoFusionAyaka') -> None:
        super().renew(new_status)
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = self.buff_desc

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If talent activated, increase cryo damage dealt by this charactor 
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
        if (
            value.damage_elemental_type != DamageElementalType.CRYO
        ):  # pragma: no cover
            # not cryo damage, do nothing
            return value
        assert mode == 'REAL'
        value.damage += 1
        return value


CryoCharactorStatus = Grimheart | CryoFusionAyaka
