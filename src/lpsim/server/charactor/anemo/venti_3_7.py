from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import SwirlChangeSummonBase

from ...event import RoundEndEventArguments

from ...action import (
    ActionTypes, Actions, ChangeObjectUsageAction, MakeDamageAction
)
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class Stormeye_3_7(SwirlChangeSummonBase):
    name: Literal['Stormeye'] = 'Stormeye'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        Need to change enemy active
        """
        ret = super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[
            self.position.player_idx].active_charactor_idx
        target_charactors = match.player_tables[
            1 - self.position.player_idx].charactors
        target_idx = our_active
        if target_charactors[target_idx].is_defeated:
            # need to choose another charactor
            for idx, charactor in enumerate(target_charactors):
                if not charactor.is_defeated:
                    target_idx = idx
                    break
            else:
                raise AssertionError('No charactor alive')
        attack_action = ret[0]
        assert attack_action.type == ActionTypes.MAKE_DAMAGE
        attack_action.charactor_change_idx[
            1 - self.position.player_idx] = target_idx
        return ret


# Skills


class SkywardSonnet(ElementalSkillBase):
    name: Literal['Skyward Sonnet'] = 'Skyward Sonnet'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        assert charactor.name == 'Venti'
        talent_activated = False
        if self.is_talent_equipped(match):
            talent_activated = True
        return super().get_actions(match) + [
            self.create_team_status(
                'Stormzone', 
                {'talent_activated': talent_activated}
            )
        ]


class WindsGrandOde(ElementalBurstBase):
    name: Literal["Wind's Grand Ode"] = "Wind's Grand Ode"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        # create summon first, so it can change element immediately.
        return [self.create_summon('Stormeye')] + super().get_actions(match)


# Talents


class EmbraceOfWinds_3_7(SkillTalent):
    name: Literal['Embrace of Winds']
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Venti'] = 'Venti'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )
    skill: Literal['Skyward Sonnet'] = 'Skyward Sonnet'


# charactor base


class Venti_3_7(CharactorBase):
    name: Literal['Venti']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SkywardSonnet | WindsGrandOde
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Divine Marksmanship',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SkywardSonnet(),
            WindsGrandOde()
        ]


register_class(Venti_3_7 | EmbraceOfWinds_3_7 | Stormeye_3_7)
