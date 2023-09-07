from typing import Any, List, Literal

from ...summon.base import DefendSummonBase

from ...modifiable_values import CombatActionValue, DamageIncreaseValue
from ...event import RoundPrepareEventArguments

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, PlayerActionLabels, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PassiveSkillBase, CharactorBase, SkillTalent
)


class Reflection(DefendSummonBase):
    name: Literal['Reflection'] = 'Reflection'
    desc: str = (
        'When your active character receives DMG: Decrease DMG taken by 1. '
        'Usage(s): 1. When the Usage is depleted, this card will not be '
        'discarded. End Phase: Discard this card, deal 1 Hydro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = False


class MirrorReflectionOfDoom(ElementalSkillBase):
    name: Literal['Mirror Reflection of Doom'] = 'Mirror Reflection of Doom'
    desc: str = '''Deals 1 Hydro DMG, summons 1 Reflection.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [self.create_summon('Reflection')]


class StellarisPhantasm(ElementalBurstBase):
    name: Literal['Stellaris Phantasm'] = 'Stellaris Phantasm'
    desc: str = '''Deals 4 Hydro DMG, creates 1 Illusory Bubble.'''
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_team_status('Illusory Bubble'))
        return ret


class IllusoryTorrent(PassiveSkillBase):
    name: Literal['Illusory Torrent'] = 'Illusory Torrent'
    desc: str = (
        '(Passive) When you perform "Switch Character" while Mona is your '
        'active character: This switch is considered a Fast Action instead of '
        'a Combat Action. (Once per Round)'
    )
    usage: int = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> CombatActionValue:
        """
        When combat action is switch, player index is self, switch from mona to
        other people, has usage, and currently is a combat action,
        change the combat action to quick action and decrease usage.
        """
        if value.action_label & PlayerActionLabels.SWITCH.value == 0:
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True,
        ):
            return value
        if self.usage <= 0:
            return value
        # as mona is active charactor, current switch is always combat action
        assert value.do_combat_action
        value.do_combat_action = False
        assert mode == 'REAL'
        self.usage -= 1
        return value


class ProphecyOfSubmersion(SkillTalent):
    name: Literal['Prophecy of Submersion']
    desc: str = (
        'Combat Action: When your active character is Mona, equip this card. '
        'When Mona equips this card, immediately use Stellaris Phantasm once. '
        'When your Mona, who has this card equipped, is the active character, '
        'the Hydro-Related Reactions you trigger deal +2 additional DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Mona'] = 'Mona'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3,
    )
    skill: StellarisPhantasm = StellarisPhantasm()

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If mona is active charactor, and damage triggered hydro reaction,
        which is made by self, increase damage by 2.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match,
            source_area = ObjectPositionType.CHARACTOR,  # quipped
            source_is_active_charactor = True,  # active charactor
            player_idx_same = True,  # self damage
        ):
            return value
        if ElementType.HYDRO not in value.reacted_elements:
            # no hydro reaction, not activate
            return value
        value.damage += 2
        return value


class Mona(CharactorBase):
    name: Literal['Mona']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Astral Reflection" Mona'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase | MirrorReflectionOfDoom | StellarisPhantasm
        | IllusoryTorrent
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT,
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: ProphecyOfSubmersion | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Ripple of Fate',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            MirrorReflectionOfDoom(),
            StellarisPhantasm(),
            IllusoryTorrent(),
        ]
