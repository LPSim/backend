from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    AOESkillBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class ClusterbloomArrow(AttackerSummonBase):
    name: Literal['Clusterbloom Arrow'] = 'Clusterbloom Arrow'
    desc: str = '''End Phase: Deal 1 Dendro DMG. (Can stack. Max 2 stacks.)'''
    version: Literal['3.6'] = '3.6'
    usage: int = 1
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    damage: int = 1
    renew_type: Literal['ADD'] = 'ADD'


# Skills


class VijnanaPhalaMine(ElementalSkillBase):
    name: Literal['Vijnana-Phala Mine'] = 'Vijnana-Phala Mine'
    desc: str = (
        'Deals 2 Dendro DMG. This character gains Vijnana Suffusion.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_charactor_status('Vijnana Suffusion'),
        ]


class FashionersTanglevineShaft(ElementalBurstBase, AOESkillBase):
    name: Literal[
        "Fashioner's Tanglevine Shaft"] = "Fashioner's Tanglevine Shaft"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    back_damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2
    )


# Talents


class KeenSight(SkillTalent):
    name: Literal['Keen Sight']
    desc: str = (
        'Combat Action: When your active character is Tighnari, equip this '
        'card. After Tighnari equips this card, immediately use Vijnana-Phala '
        'Mine once. When your Tighnari, who has this card equipped, is '
        "affected by Vijnana Suffusion, the character's Charged Attack costs "
        '1 less Unaligned Element.'
    )
    version: Literal['3.6'] = '3.6'
    charactor_name: Literal['Tighnari'] = 'Tighnari'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 4,
    )
    skill: VijnanaPhalaMine = VijnanaPhalaMine()


# charactor base


class Tighnari(CharactorBase):
    name: Literal['Tighnari']
    version: Literal['3.6'] = '3.6'
    desc: str = '''"Verdant Strider" Tighnari'''
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | VijnanaPhalaMine | FashionersTanglevineShaft
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.BOW
    talent: KeenSight | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Khanda Barrier-Buster',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            VijnanaPhalaMine(),
            FashionersTanglevineShaft()
        ]
