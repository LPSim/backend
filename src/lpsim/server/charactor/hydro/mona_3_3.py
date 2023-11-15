from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DefendSummonBase

from ...modifiable_values import CombatActionValue, DamageIncreaseValue
from ...event import RoundPrepareEventArguments

from ...action import Actions
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, ObjectPositionType, PlayerActionLabels, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PassiveSkillBase, CharactorBase, SkillTalent
)


class Reflection_3_3(DefendSummonBase):
    name: Literal['Reflection'] = 'Reflection'
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


class ProphecyOfSubmersion_3_3(SkillTalent):
    name: Literal['Prophecy of Submersion']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Mona'] = 'Mona'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3,
    )
    skill: Literal['Stellaris Phantasm'] = 'Stellaris Phantasm'

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


class Mona_3_3(CharactorBase):
    name: Literal['Mona']
    version: Literal['3.3'] = '3.3'
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

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Ripple of Fate',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            MirrorReflectionOfDoom(),
            StellarisPhantasm(),
            IllusoryTorrent(),
        ]


register_class(Mona_3_3 | ProphecyOfSubmersion_3_3 | Reflection_3_3)
