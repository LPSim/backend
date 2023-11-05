# type: ignore


from typing import Any, List, Literal

from ..old_version.talent_cards_4_2 import LightningStorm_3_4

from ...modifiable_values import CostValue
from ...event import ReceiveDamageEventArguments, RoundPrepareEventArguments

from ...action import Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.
# Round status, will last for several rounds and disappear
# Skills


class Tidecaller(ElementalSkillBase):
    name: Literal['Tidecaller'] = 'Tidecaller'
    desc: str = (
        'This character gains a Tidecaller: Surf Embrace. '
        'Prepare Skill: Wavestrider.'
    )
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create status
        """
        return [
            self.charge_self(1),
            self.create_charactor_status('Tidecaller: Surf Embrace'),
        ]


class Wavestrider(ElementalSkillBase):
    name: Literal['Wavestrider'] = 'Wavestrider'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        alway invalid to directly use.
        """
        return False

    def get_actions(self, match: Any) -> List[MakeDamageAction]:
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type)
        ]


class Stormbreaker(ElementalBurstBase):
    name: Literal['Stormbreaker'] = 'Stormbreaker'
    desc: str = (
        "Deals _DAMAGE_ Electro DMG, creates 1 Thunderbeast's Targe."
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status("Thunderbeast's Targe"),
        ]


# Talents


class LightningStorm(LightningStorm_3_4):
    desc: str = (
        'Combat Action: When your active character is Beidou, equip this '
        'card. After Beidou equips this card, immediately use Tidecaller '
        'once. When Beidou, who has this card equipped, uses Wavestrider: '
        "Beidou's Normal Attacks this Round will cost 1 less Unaligned "
        'Element. (Can be triggered 2 times)'
    )
    version: Literal['4.2'] = '4.2'
    need_to_activate: bool = False


# charactor base


class Beidou(CharactorBase):
    name: Literal['Beidou']
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Uncrowned Lord of the Ocean" Beidou'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | Tidecaller | Wavestrider | Stormbreaker
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: LightningStorm | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Oceanborne',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Tidecaller(),
            Wavestrider(),
            Stormbreaker(),
        ]
