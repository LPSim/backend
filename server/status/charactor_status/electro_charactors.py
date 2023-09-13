from typing import Any, List, Literal

from ...struct import Cost

from ...action import (
    Actions, MakeDamageAction, RemoveObjectAction, SkillEndAction
)

from ...event import MakeDamageEventArguments, SkillEndEventArguments

from ...consts import (
    DamageElementalType, DamageType, DieColor, ObjectPositionType, SkillType
)

from ...modifiable_values import CostValue, DamageIncreaseValue, DamageValue
from .base import (
    ElementalInfusionCharactorStatus, PrepareCharactorStatus, 
    RoundCharactorStatus, UsageCharactorStatus, CharactorStatusBase
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
        'Physical Damage, it will be turned into Electro DMG, '
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
        super().renew(new_status)
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


class ChakraDesiderata(CharactorStatusBase):
    name: Literal['Chakra Desiderata'] = 'Chakra Desiderata'
    desc: str = (
        'After your other characters use Elemental Bursts: Gain 1 Resolve. '
        '(Max 3) '
        'When the character to which this is attached uses Secret Art: Musou '
        'Shinsetsu: Consume all Resolve and deal +1 DMG per Resolve.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 0
    max_usage: int = 3

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        When other charactor using elemental burst, gain resolve.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = False, target_area = ObjectPositionType.SKILL,
        ):
            # not other ally use elemental burst, do nothing
            return []
        if event.action.skill_type == SkillType.ELEMENTAL_BURST:
            # is burst
            self.usage = min(self.usage + 1, self.max_usage)
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When self using elemental burst, increase damage by usage.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_BURST
        ):
            # not self use burst, do nothing
            return value
        # increase damage
        value.damage += self.usage
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.talent is not None:
            # has talent, double increase damage
            value.damage += self.usage
        self.usage = 0
        return value


class TheShrinesSacredShade(RoundCharactorStatus):
    # TODO Rite of Dispatch
    name: Literal["The Shrine's Sacred Shade"] = "The Shrine's Sacred Shade"
    desc: str = (
        'During this round, the next Yakan Evocation: Sesshou Sakura used by '
        'the charactor to which this is attached will cost 2 less Elemental '
        'Dice.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        When use Yakan Evocation: Sesshou Sakura, cost 2 less
        """
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True,
            target_area = ObjectPositionType.SKILL
        ):
            # not our player skill, do nothing
            return value
        skill = match.get_object(value.position)
        if skill.name != 'Yakan Evocation: Sesshou Sakura':
            # not right skill, do nothing
            return value
        assert self.usage > 0
        success = value.cost.decrease_cost(DieColor.ELECTRO)
        success = value.cost.decrease_cost(DieColor.ELECTRO) or success
        if success and mode == 'REAL':
            self.usage -= 1
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndAction, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


ElectroCharactorStatus = (
    ElectroInfusionKeqing | RockPaperScissorsComboScissors
    | RockPaperScissorsComboPaper | ElectroCrystalCore | ChakraDesiderata
    | TheShrinesSacredShade
)
