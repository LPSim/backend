from typing import Any, List, Literal

from ...struct import Cost

from ...action import (
    Actions, ChangeObjectUsageAction, MakeDamageAction, RemoveObjectAction, 
    SkillEndAction
)

from ...event import (
    ChangeObjectUsageEventArguments, MakeDamageEventArguments, 
    RoundEndEventArguments, SkillEndEventArguments
)

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, IconType, 
    ObjectPositionType, SkillType
)

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue, DamageValue
)
from .base import (
    ElementalInfusionCharactorStatus, PrepareCharactorStatus, 
    ReviveCharactorStatus, RoundCharactorStatus, ShieldCharactorStatus, 
    UsageCharactorStatus, CharactorStatusBase
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


class ElectroCrystalCore(ReviveCharactorStatus):
    name: Literal['Electro Crystal Core'] = 'Electro Crystal Core'
    version: Literal['3.7'] = '3.7'
    heal: int = 1


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
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

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
    name: Literal["The Shrine's Sacred Shade"] = "The Shrine's Sacred Shade"
    desc: str = (
        'During this round, the next Yakan Evocation: Sesshou Sakura used by '
        'the charactor to which this is attached will cost 2 less Elemental '
        'Dice.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

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


class TheWolfWithin(RoundCharactorStatus):
    name: Literal['The Wolf Within'] = 'The Wolf Within'
    desc: str = (
        'After the character to which this is attached uses a Normal Attack '
        'or an Elemental Skill: Deal 2 Electro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self use normal attack or elemental skill, deal damage
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL
        ):
            # not self use skill
            return []
        if event.action.skill_type not in [
            SkillType.NORMAL_ATTACK, SkillType.ELEMENTAL_SKILL
        ]:
            # not normal attack or elemental skill
            return []
        # make damage
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target.position,
                    damage = 2,
                    damage_elemental_type = DamageElementalType.ELECTRO,
                    cost = Cost()
                )
            ]
        )]


class TidecallerSurfEmbrace(ShieldCharactorStatus, PrepareCharactorStatus):
    name: Literal['Tidecaller: Surf Embrace'] = 'Tidecaller: Surf Embrace'
    desc: str = (
        'The next time this character acts, they will immediately use the '
        'Skill Wavestrider. While preparing this Skill: Grant 2 Shield '
        'points to the character to which this is attached.'
    )
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Beidou'] = 'Beidou'
    skill_name: Literal['Wavestrider'] = 'Wavestrider'

    usage: int = 2
    max_usage: int = 2

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        Do not remove when usage becomes zero
        """
        return []


class CrowfeatherCover(UsageCharactorStatus):
    name: Literal['Crowfeather Cover'] = 'Crowfeather Cover'
    desc: str = (
        'The character with this attached deals +1 Elemental Skill and '
        'Elemental Burst DMG.'
    )
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if value.damage_from_element_reaction:
            # is elemental reaction, do nothing
            return value
        if (
            value.is_corresponding_charactor_use_damage_skill(
                self.position, match, SkillType.ELEMENTAL_SKILL
            )
            or value.is_corresponding_charactor_use_damage_skill(
                self.position, match, SkillType.ELEMENTAL_BURST
            )
        ):
            # is self use elemental skill or elemental burst
            if self.usage <= 0:  # pragma: no cover
                # no usage
                return value
            # increase damage
            assert mode == 'REAL'
            self.usage -= 1
            value.damage += 1
            # talent effects
            charactors = match.player_tables[
                self.position.player_idx].charactors
            if (
                charactors[self.position.charactor_idx].element 
                != ElementType.ELECTRO
            ):
                # not electro
                return value
            found_talent_kujou: bool = False
            for charactor in charactors:
                if (
                    charactor.name == 'Kujou Sara' 
                    and charactor.talent is not None
                ):
                    found_talent_kujou = True
                    break
            if found_talent_kujou:
                # increase one more damage
                value.damage += 1
        return value


class PactswornPathclearer(ElementalInfusionCharactorStatus):
    name: Literal['Pactsworn Pathclearer'] = 'Pactsworn Pathclearer'
    desc: str = (
        'End Phase: Gain 1 level of Indwelling. '
        'Create the following effects based on the Indwelling Level: '
        'If equal to or greater than 2: Physical DMG dealt is converted to '
        'Electro DMG; If equal or greater than 4: DMG dealt +2; If equal to '
        'or greater than 6: Indwelling Level -4'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 0
    max_usage: int = 999
    infused_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        if self.usage < 2:
            # level not enough
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode)

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if self.usage < 4:
            # level not enough
            return value
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # self use skill, increase damage
            assert mode == 'REAL'
            value.damage += 2
        return value

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        add one usage
        """
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Any
    ) -> List[Actions]:
        """
        When change object usage, check if usage is greater than 6.
        If so, decrease by 4.
        """
        if self.usage >= 6:
            self.usage -= 4
        return []


class Conductive(CharactorStatusBase):
    """
    repeatedly attach, end phase accumulate will perform in this status;
    damage increase will perform in elemental skill.
    """
    name: Literal['Conductive'] = 'Conductive'
    desc: str = (
        'This status starts with 2 stacks of Conductive. When attached '
        'repeatedly, Conductive stack +1. Conductive can be stacked to a '
        'maximum of 4 stacks. End Phase: Accumulate 1 stack of Conductive. '
        'When the character attached with Conductive takes DMG from Violet '
        'Arc: Remove this status and DMG +1 for each stack of Conductive. '
    )
    version: Literal['4.0'] = '4.0'
    usage: int = 2
    max_usage: int = 4
    icon_type: Literal[IconType.DEBUFF] = IconType.DEBUFF

    def renew(self, new_status: 'Conductive'):
        """
        Add one usage
        """
        self.usage = min(self.max_usage, self.usage + 1)

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round end, add one usage
        """
        self.usage = min(self.max_usage, self.usage + 1)
        return []


ElectroCharactorStatus = (
    ElectroInfusionKeqing | RockPaperScissorsComboScissors
    | RockPaperScissorsComboPaper | ElectroCrystalCore | ChakraDesiderata
    | TheShrinesSacredShade | TheWolfWithin | TidecallerSurfEmbrace
    | CrowfeatherCover | PactswornPathclearer | Conductive
)
