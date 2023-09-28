from typing import Any, List, Literal

from ...modifiable_values import DamageIncreaseValue

from ...summon.base import AttackerSummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, SkillType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class GardenOfPurity(AttackerSummonBase):
    name: Literal['Garden of Purity'] = 'Garden of Purity'
    desc: str = (
        'End Phase: Deal 2 Hydro DMG. '
        "When this summon is on the field: Your characters' Normal Attacks "
        'deal +1 DMG.'
    )
    version: Literal['3.6'] = '3.6'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            assert mode == 'REAL'
            value.damage += 1
        return value


# Skills


class KamisatoArtKyouka(ElementalSkillBase):
    name: Literal['Kamisato Art: Kyouka'] = 'Kamisato Art: Kyouka'
    desc: str = '''Deals 2 Hydro DMG. This Character gains Takimeguri Kanka.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_charactor_status(
                'Takimeguri Kanka',
                {
                    'usage': 3,
                    'max_usage': 3
                }
            ),
        ]


class KamisatoArtSuiyuu(ElementalBurstBase):
    name: Literal['Kamisato Art: Suiyuu'] = 'Kamisato Art: Suiyuu'
    desc: str = '''Deals 1 Hydro DMG, summons 1 Garden of Purity.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Garden of Purity')
        ]


# Talents


class KyoukaFuushi(SkillTalent):
    name: Literal['Kyouka Fuushi']
    desc: str = (
        'Combat Action: When your active character is Kamisato Ayato, equip '
        'this card. After Kamisato Ayato equips this card, immediately use '
        'Kamisato Art: Kyouka once. When your Kamisato Ayato, who has this '
        'card equipped, triggers the effects of Takimeguri Kanka, deal +1 '
        "additional DMG if the target's remaining HP is equal to or less "
        'than 6.'
    )
    version: Literal['3.6'] = '3.6'
    charactor_name: Literal['Kamisato Ayato'] = 'Kamisato Ayato'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: KamisatoArtKyouka = KamisatoArtKyouka()


# charactor base


class KamisatoAyato(CharactorBase):
    name: Literal['Kamisato Ayato']
    version: Literal['4.1'] = '4.1'
    desc: str = '''"Pillar of Fortitude" Kamisato Ayato'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | KamisatoArtKyouka | KamisatoArtSuiyuu
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: KyoukaFuushi | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Kamisato Art: Marobashi',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            KamisatoArtKyouka(),
            KamisatoArtSuiyuu(),
        ]
