from typing import Any, List, Literal

from ...modifiable_values import DamageIncreaseValue, DamageValue
from ...action import Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class GuideToAfterlife(ElementalSkillBase):
    name: Literal['Guide to Afterlife'] = 'Guide to Afterlife'
    desc: str = '''This character gains Paramita Papilio.'''
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        gain charge and create status
        """
        return [
            self.charge_self(1),
            self.create_charactor_status('Paramita Papilio'),
        ]


class SpiritSoother(ElementalBurstBase):
    name: Literal['Spirit Soother'] = 'Spirit Soother'
    desc: str = (
        "Deals 4 Pyro DMG, heals herself for 2 HP. If this character's HP is "
        "no more than 6, DMG dealt and Healing are increased by 1."
    )
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Check if hp <= 6. If so, increase damage and heal
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        heal = 2
        if charactor.hp <= 6:
            self.damage = 5
            heal = 3
        ret = super().get_actions(match)
        self.damage = 4
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -heal,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                )
            ]
        ))
        return ret

# Talents


class SanguineRouge(SkillTalent):
    name: Literal['Sanguine Rouge']
    desc: str = (
        'Combat Action: When your active character is Hu Tao, equip this '
        'card. After Hu Tao equips this card, immediately use Guide to '
        'Afterlife once. When your Hu Tao, who has this card equipped, has no '
        'more than 6 HP, Pyro DMG dealt +1.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Hu Tao'] = 'Hu Tao'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2
    )
    skill: GuideToAfterlife = GuideToAfterlife()

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self use damage skill
            return value
        if value.damage_elemental_type != DamageElementalType.PYRO:
            # not pyro damage
            return value
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp > 6:
            # hp > 6
            return value
        # increase damage
        value.damage += 1
        return value


# charactor base


class HuTao(CharactorBase):
    name: Literal['Hu Tao']
    version: Literal['3.7'] = '3.7'
    desc: str = '''"Fragrance in Thaw" Hu Tao'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | GuideToAfterlife | SpiritSoother
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: SanguineRouge | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Secret Spear of Wangsheng',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GuideToAfterlife(),
            SpiritSoother()
        ]
