from typing import Any, List, Literal

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear


# Skills


class SacredRiteHeronsSanctum(ElementalSkillBase):
    name: Literal[
        "Sacred Rite: Heron's Sanctum"] = "Sacred Rite: Heron's Sanctum"
    desc: str = (
        'Attaches a Heron Shield to this character and prepares Heron Strike'
    )
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        prepare
        """
        return [
            self.charge_self(1),
            self.create_charactor_status('Heron Shield'),
        ]


class HeronStrike(ElementalSkillBase):
    name: Literal['Heron Strike'] = 'Heron Strike'
    desc: str = '''(Prepare for 1 turn) Deals 3 Hydro DMG.'''
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        alway invalid to directly use.
        """
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        """
        no charge, only attack
        """
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type)
        ]


class SacredRiteWagtailsTide(ElementalBurstBase):
    name: Literal[
        "Sacred Rite: Wagtail's Tide"] = "Sacred Rite: Wagtail's Tide"
    desc: str = '''Deals 2 Hydro DMG and create Prayer of the Crimson Crown.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status('Prayer of the Crimson Crown'),
        ]


# Talents


class TheOverflow(SkillTalent):
    name: Literal['The Overflow']
    desc: str = (
        'Combat Action: When your active character is Candace, equip this '
        'card. After Candace equips this card, immediately use Sacred Rite: '
        "Wagtail's Tide once. When this card is equipped by Candace, her "
        'Prayer of the Crimson Crown has the following extra effect: After '
        'your character uses a Normal Attack: Deals 1 Hydro DMG. (Once per '
        'Round)'
    )
    version: Literal['3.8'] = '3.8'
    charactor_name: Literal['Candace'] = 'Candace'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: SacredRiteWagtailsTide = SacredRiteWagtailsTide()


# charactor base


class Candace(CharactorBase):
    name: Literal['Candace']  # Do not set default value for charactor name
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Golden Vow" Candace'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SacredRiteHeronsSanctum 
        | SacredRiteWagtailsTide | HeronStrike
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: TheOverflow | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Gleaming Spear - Guardian Stance',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SacredRiteHeronsSanctum(),
            SacredRiteWagtailsTide(),
            HeronStrike(),
        ]
