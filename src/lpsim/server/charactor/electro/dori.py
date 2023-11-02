from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...event import RoundEndEventArguments

from ...action import Actions, ChargeAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class AfterSalesServiceRounds(AttackerSummonBase):
    name: Literal['After-Sales Service Rounds'] = 'After-Sales Service Rounds'
    version: Literal['4.2'] = '4.2'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1


class Jinni(AttackerSummonBase):
    name: Literal['Jinni'] = 'Jinni'
    version: Literal['4.2'] = '4.2'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HEAL
    damage: int = -2
    talent_activated: bool = False

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChargeAction]:
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        charge = 1
        if self.talent_activated:
            if active_charactor.hp <= 6:
                self.damage = -3
            if active_charactor.charge == 0:
                charge = 2
        ret = super().event_handler_ROUND_END(event, match) + [
            ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = active_charactor.position.charactor_idx,
                charge = charge,
            )
        ]
        self.damage = -2
        return ret


# Skills


class SpiritWaridingLampTroubleshooterCannon(ElementalSkillBase):
    name: Literal[
        'Spirit-Warding Lamp: Troubleshooter Cannon'
    ] = 'Spirit-Warding Lamp: Troubleshooter Cannon'
    desc: str = (
        'Deals 2 Electro DMG, summons 1 After-Sales Service Rounds.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('After-Sales Service Rounds')]


class AlcazarzaraysExactitude(ElementalBurstBase):
    name: Literal["Alcazarzaray's Exactitude"] = "Alcazarzaray's Exactitude"
    desc: str = (
        'Deals 1 Electro DMG, summons 1 Jinni.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Jinni', {
                'talent_activated': self.is_talent_equipped(match)
            })]


# Talents


class DiscretionarySupplement(SkillTalent):
    name: Literal['Discretionary Supplement']
    desc: str = (
        'Combat Action: When your active character is Dori, equip this card. '
        "After Dori equips this card, immediately use Alcazarzaray's "
        'Exactitude once. The Jinni summoned by your Dori who has this card '
        'equipped heals 1 more HP when healing characters with no more than '
        '6 HP, and increases the amount of Energy gained by characters with '
        'no Energy by 1 when Energy is gained.'
    )
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Dori'] = 'Dori'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: AlcazarzaraysExactitude = AlcazarzaraysExactitude()


# charactor base


class Dori(CharactorBase):
    name: Literal['Dori']
    version: Literal['4.2'] = '4.2'
    desc: str = '''"Treasure of Dream Garden" Dori'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SpiritWaridingLampTroubleshooterCannon 
        | AlcazarzaraysExactitude
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: DiscretionarySupplement | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Marvelous Sword-Dance (Modified)',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SpiritWaridingLampTroubleshooterCannon(),
            AlcazarzaraysExactitude()
        ]
