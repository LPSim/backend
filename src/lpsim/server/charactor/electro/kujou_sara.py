from typing import Any, List, Literal

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class TenguJuuraiAmbush(AttackerSummonBase):
    name: Literal['Tengu Juurai: Ambush'] = 'Tengu Juurai: Ambush'
    desc: str = (
        'End Phase: Deal _DAMAGE_ Electro DMG, applies Crowfeather Cover to '
        'friendly active character.'
    )
    version: Literal['3.5'] = '3.5'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | CreateObjectAction]:
        ret: List[MakeDamageAction | CreateObjectAction] = []
        ret += super().event_handler_ROUND_END(event, match)
        active_idx = match.player_tables[
            self.position.player_idx].active_charactor_idx
        ret.append(CreateObjectAction(
            object_name = 'Crowfeather Cover',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                charactor_idx = active_idx,
                area = ObjectPositionType.CHARACTOR_STATUS,
                id = -1
            ),
            object_arguments = {}
        ))
        return ret


class TenguJuuraiStormcluster(TenguJuuraiAmbush):
    name: Literal['Tengu Juurai: Stormcluster'] = 'Tengu Juurai: Stormcluster'
    usage: int = 2
    max_usage: int = 2
    damage: int = 2


# Skills


class TenguStormcall(ElementalSkillBase):
    name: Literal['Tengu Stormcall'] = 'Tengu Stormcall'
    desc: str = '''Deals 1 Electro DMG, summons 1 Tengu Juurai: Ambush.'''
    damage: int = 1
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
            self.create_summon('Tengu Juurai: Ambush')
        ]


class SubjugationKoukouSendou(ElementalBurstBase):
    name: Literal['Subjugation: Koukou Sendou'] = 'Subjugation: Koukou Sendou'
    desc: str = (
        'Deals 1 Electro DMG, summons 1 Tengu Juurai: Stormcluster.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('Tengu Juurai: Stormcluster')
        ]


# Talents


class SinOfPride(SkillTalent):
    name: Literal['Sin of Pride']
    desc: str = (
        'Combat Action: When your active character is Kujou Sara, equip this '
        'card. After Kujou Sara equips this card, immediately use '
        'Subjugation: Koukou Sendou once. When Kujou Sara is active and has '
        'this card equipped, all allied Electro characters with Crowfeather '
        'Cover will deal +1 additional Elemental Skill and Elemental Burst '
        'DMG.'
    )
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Kujou Sara'] = 'Kujou Sara'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: SubjugationKoukouSendou = SubjugationKoukouSendou()


# charactor base


class KujouSara(CharactorBase):
    name: Literal['Kujou Sara']
    version: Literal['3.5'] = '3.5'
    desc: str = '''"Crowfeather Kaburaya" Kujou Sara'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | TenguStormcall | SubjugationKoukouSendou
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.BOW
    talent: SinOfPride | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Tengu Bowmanship',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TenguStormcall(),
            SubjugationKoukouSendou()
        ]
