from typing import Any, List, Literal

from ...struct import Cost

from ...action import MakeDamageAction, RemoveObjectAction

from ...event import MakeDamageEventArguments

from ...consts import DamageElementalType, DamageType

from ...modifiable_values import DamageIncreaseValue, DamageValue
from .base import (
    ElementalInfusionCharactorStatus, PrepareCharactorStatus, 
    RoundCharactorStatus, UsageCharactorStatus
)


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


class ElectroCrystalCore(UsageCharactorStatus):
    name: Literal['Electro Crystal Core'] = 'Electro Crystal Core'
    desc: str = (
        'When the character to which this is attached would be defeated: '
        'Remove this effect, ensure the character will not be defeated, and '
        'heal them to 1 HP.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        when make damage, check whether this charactor's hp is 0. if so,
        heal it by 1 hp.

        Using make damage action, so it will trigger immediately before
        receiving any other damage, and can be defeated by other damage.
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp > 0:
            # hp not 0, do nothing
            return []
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return []
        # heal this charactor by 1
        self.usage -= 1
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                )
            ],
        )] + self.check_should_remove()


class RockPaperScissorsComboScissors(PrepareCharactorStatus):
    name: Literal[
        'Rock-Paper-Scissors Combo: Scissors'
    ] = 'Rock-Paper-Scissors Combo: Scissors'
    desc: str = (
        'Prepare Skill Rock-Paper-Scissors Combo: Scissors and '
        'Rock-Paper-Scissors Combo: Paper.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Electro Hypostasis'] = 'Electro Hypostasis'
    skill_name: Literal[
        'Rock-Paper-Scissors Combo: Scissors'
    ] = 'Rock-Paper-Scissors Combo: Scissors'


class RockPaperScissorsComboPaper(PrepareCharactorStatus):
    name: Literal[
        'Rock-Paper-Scissors Combo: Paper'
    ] = 'Rock-Paper-Scissors Combo: Paper'
    desc: str = (
        'Prepare Skill Rock-Paper-Scissors Combo: Paper.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Electro Hypostasis'] = 'Electro Hypostasis'
    skill_name: Literal[
        'Rock-Paper-Scissors Combo: Paper'
    ] = 'Rock-Paper-Scissors Combo: Paper'


ElectroCharactorStatus = (
    ElectroInfusionKeqing | RockPaperScissorsComboScissors
    | RockPaperScissorsComboPaper | ElectroCrystalCore
)
