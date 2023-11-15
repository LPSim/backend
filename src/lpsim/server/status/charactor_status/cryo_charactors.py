
from typing import Any, Literal

from ....utils.class_registry import register_class

from ...consts import DamageElementalType, IconType, SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import (
    ElementalInfusionCharactorStatus, RoundCharactorStatus, 
    UsageCharactorStatus
)


class Grimheart_3_8(UsageCharactorStatus):
    name: Literal['Grimheart'] = 'Grimheart'
    version: Literal['3.8'] = '3.8'
    damage: int = 3
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP_ICE] = IconType.ATK_UP_ICE

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.version == '3.5':
            self.damage = 2
        else:
            assert self.version == '3.8'
            self.damage = 3

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


class Grimheart_3_5(Grimheart_3_8):
    version: Literal['3.5']
    damage: int = 2


class CryoFusionAyaka_3_3(ElementalInfusionCharactorStatus,
                          RoundCharactorStatus):
    """
    Inherit from vanilla elemental infusion status, and has talent activated
    argument. when talent activated, it will gain electro damage +1 buff,
    and usage +1.
    """
    name: Literal['Cryo Elemental Infusion'] = 'Cryo Elemental Infusion'
    mark: Literal['Kamisato Ayaka']  # used to select right status
    desc: Literal['', 'ayaka_talent'] = ''
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    talent_activated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.talent_activated:
            self.desc = 'ayaka_talent'

    def renew(self, new_status: 'CryoFusionAyaka_3_3') -> None:
        super().renew(new_status)
        if new_status.talent_activated:
            self.talent_activated = True
            self.desc = 'ayaka_talent'

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


register_class(Grimheart_3_8 | Grimheart_3_5 | CryoFusionAyaka_3_3)
