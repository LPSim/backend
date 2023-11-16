from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DeclareRoundEndAttackSummonBase

from ...modifiable_values import DamageIncreaseValue

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, PhysicalNormalAttackBase, 
    CharactorBase, SkillTalent
)


# Summons


class BounatifulCore_4_2(DeclareRoundEndAttackSummonBase):
    name: Literal['Bountiful Core'] = 'Bountiful Core'
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 2
    renew_type: Literal['ADD'] = 'ADD'
    extra_attack_usage: int = 2


# Skills


class DanceOfHaftkarsvar(ElementalSkillBase):
    name: Literal['Dance of Haftkarsvar'] = 'Dance of Haftkarsvar'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        all_hydro_dendro = True
        charactors = match.player_tables[self.position.player_idx].charactors
        for c in charactors:
            if (
                c.element != ElementType.HYDRO 
                and c.element != ElementType.DENDRO
            ):
                all_hydro_dendro = False
                break
        ret = super().get_actions(match)
        if all_hydro_dendro:
            # first generate team status, then attack
            ret = [
                self.create_team_status('Golden Chalice\'s Bounty')
            ] + ret
        return ret


class DanceOfAbzendegiDistantDreamsListeningSpring(ElementalBurstBase):
    name: Literal[
        'Dance of Abzendegi: Distant Dreams, Listening Spring'
    ] = 'Dance of Abzendegi: Distant Dreams, Listening Spring'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_opposite_charactor_status(
                match, 'Lingering Aeon', {}
            )
        ]


# Talents


class TheStarrySkiesTheirFlowersRain_4_2(SkillTalent):
    name: Literal['The Starry Skies Their Flowers Rain']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Nilou'] = 'Nilou'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: Literal['Dance of Haftkarsvar'] = 'Dance of Haftkarsvar'

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        When self Bountiful Core damage, increase damage by 1
        """
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SUMMON,
        ):
            # not equipped, or source not self summon
            return value
        summon = match.get_object(value.position)
        if summon is None or summon.name != 'Bountiful Core':
            # not Bountyful Core
            return value
        # damage +1
        value.damage += 1
        return value


# charactor base


class Nilou_4_2(CharactorBase):
    name: Literal['Nilou']
    version: Literal['4.2'] = '4.2'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | DanceOfHaftkarsvar 
        | DanceOfAbzendegiDistantDreamsListeningSpring
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Dance of Samser',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            DanceOfHaftkarsvar(),
            DanceOfAbzendegiDistantDreamsListeningSpring(),
        ]


register_class(
    Nilou_4_2 | TheStarrySkiesTheirFlowersRain_4_2 | BounatifulCore_4_2
)
