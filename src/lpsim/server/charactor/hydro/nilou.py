from typing import Any, List, Literal

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


class BounatifulCore(DeclareRoundEndAttackSummonBase):
    name: Literal['Bountiful Core'] = 'Bountiful Core'
    desc: str = (
        'End Phase: Deal 2 Dendro DMG. Usage(s): 1 (Can stack, max 3 stacks) '
        'When you declare the end of your Round: If this summon has at least '
        '2 Usages remaining, deal 2 Dendro DMG. (Consumes Usages)'
    )
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
    desc: str = (
        'Deals 3 Hydro DMG, if the party includes Hydro Characters and Dendro '
        'Characters and characters from no other Elements, create 1 Golden '
        "Chalice's Bounty."
    )
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
            ret.append(
                self.create_team_status('Golden Chalice\'s Bounty')
            )
        return ret


class DanceOfAbzendegiDistantDreamsListeningSpring(ElementalBurstBase):
    name: Literal[
        'Dance of Abzendegi: Distant Dreams, Listening Spring'
    ] = 'Dance of Abzendegi: Distant Dreams, Listening Spring'
    desc: str = (
        'Deals 2 Hydro DMG. The target character receives Lingering Aeon.'
    )
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


class TheStarrySkiesTheirFlowersRain(SkillTalent):
    name: Literal['The Starry Skies Their Flowers Rain']
    desc: str = (
        'Combat Action: When your active character is Nilou, equip this card. '
        'After Nilou equips this card, immediately use Dance of Haftkarsvar. '
        'When there is Nilou on the field who has this card equipped, the '
        'damage dealt by your Bountiful Core is increased by 1. '
    )
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Nilou'] = 'Nilou'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: DanceOfHaftkarsvar = DanceOfHaftkarsvar()

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
        if summon.name != 'Bountiful Core':
            # not Bountyful Core
            return value
        # damage +1
        value.damage += 1
        return value


# charactor base


class Nilou(CharactorBase):
    name: Literal['Nilou']
    version: Literal['4.2'] = '4.2'
    desc: str = '''"Dance of Lotuslight" Nilou'''
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
    talent: TheStarrySkiesTheirFlowersRain | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Dance of Samser',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            DanceOfHaftkarsvar(),
            DanceOfAbzendegiDistantDreamsListeningSpring(),
        ]
