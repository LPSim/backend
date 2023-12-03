from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...action import (
    Actions, ChangeObjectUsageAction, CreateObjectAction, MakeDamageAction
)
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


class TenguJuuraiAmbush_3_5(AttackerSummonBase):
    name: Literal['Tengu Juurai: Ambush'] = 'Tengu Juurai: Ambush'
    version: Literal['3.5'] = '3.5'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | CreateObjectAction | ChangeObjectUsageAction]:
        ret: List[
            MakeDamageAction | CreateObjectAction | ChangeObjectUsageAction
        ] = []
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


class TenguJuuraiStormcluster_3_5(TenguJuuraiAmbush_3_5):
    name: Literal['Tengu Juurai: Stormcluster'] = 'Tengu Juurai: Stormcluster'
    usage: int = 2
    max_usage: int = 2
    damage: int = 2


# Skills


class TenguStormcall(ElementalSkillBase):
    name: Literal['Tengu Stormcall'] = 'Tengu Stormcall'
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


class SinOfPride_3_5(SkillTalent):
    name: Literal['Sin of Pride']
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Kujou Sara'] = 'Kujou Sara'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: Literal['Subjugation: Koukou Sendou'] = 'Subjugation: Koukou Sendou'


class SinOfPride_4_2(SkillTalent):
    name: Literal['Sin of Pride']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Kujou Sara'] = 'Kujou Sara'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Tengu Stormcall'] = 'Tengu Stormcall'


# charactor base


class KujouSara_3_5(CharactorBase):
    name: Literal['Kujou Sara']
    version: Literal['3.5'] = '3.5'
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

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Tengu Bowmanship',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TenguStormcall(),
            SubjugationKoukouSendou()
        ]


register_class(
    KujouSara_3_5 | SinOfPride_3_5 | SinOfPride_4_2 | TenguJuuraiAmbush_3_5 
    | TenguJuuraiStormcluster_3_5
)
