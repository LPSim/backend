from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import SummonBase

from ...modifiable_values import DamageValue
from ...event import RoundEndEventArguments

from ...action import (
    Actions, ChangeObjectUsageAction, MakeDamageAction, RemoveObjectAction
)
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    IconType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Summons


class LightfallSword_3_8(SummonBase):
    name: Literal['Lightfall Sword'] = 'Lightfall Sword'
    version: Literal['3.8'] = '3.8'
    usage: int = 0
    max_usage: int = 999
    damage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.PHYSICAL
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        When round end, make damage to the opponent and remove self
        """
        player_idx = self.position.player_idx
        target_table = match.player_tables[1 - player_idx]
        target_charactor = target_table.get_active_charactor()
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target_charactor.position,
                        damage = self.damage + self.usage,
                        damage_elemental_type = self.damage_elemental_type,
                        cost = Cost(),
                    )
                ],
            ),
            RemoveObjectAction(
                object_position = self.position,
            )
        ]


# Skills


class FavoniusBladeworkEdel(PhysicalNormalAttackBase):
    name: Literal['Favonius Bladework - Edel'] = 'Favonius Bladework - Edel'
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.CRYO)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If summon Lightfall Sword exists, not charge but add two usage.
        """
        summons = match.player_tables[self.position.player_idx].summons
        LS_idx = -1
        for sidx, summon in enumerate(summons):
            if summon.name == 'Lightfall Sword':
                LS_idx = sidx
                break
        ret: List[Actions] = []
        ret.append(self.attack_opposite_active(
            match, self.damage, self.damage_type))
        if LS_idx != -1:
            # add LS usage
            ret.append(ChangeObjectUsageAction(
                object_position = summons[LS_idx].position,
                change_usage = 2,
            ))
        else:
            # charge
            ret.append(self.charge_self(1))
        return ret


class IcetideVortex(ElementalSkillBase):
    name: Literal['Icetide Vortex'] = 'Icetide Vortex'
    version: Literal['3.8'] = '3.8'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If summon Lightfall Sword exists, not charge but add two or three 
        usage, based on whether has talent.
        """
        summons = match.player_tables[self.position.player_idx].summons
        LS_idx = -1
        for sidx, summon in enumerate(summons):
            if summon.name == 'Lightfall Sword':
                LS_idx = sidx
                break
        ret: List[Actions] = []
        ret.append(self.attack_opposite_active(
            match, self.damage, self.damage_type))
        if LS_idx != -1:
            # add LS usage
            usage = 2
            if self.is_talent_equipped(match):
                # has talent, add one more
                usage = 3
            ret.append(ChangeObjectUsageAction(
                object_position = summons[LS_idx].position,
                change_usage = usage,
            ))
        else:
            # charge
            ret.append(self.charge_self(1))
        status = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx].status
        for s in status:
            if s.name == 'Grimheart':
                # has Grimheart, return
                return ret
        # no Grimheart, add Grimheart
        ret.append(self.create_charactor_status(
            'Grimheart', { 'version': self.version }))
        return ret


class GlacialIllumination(ElementalBurstBase):
    name: Literal['Glacial Illumination'] = 'Glacial Illumination'
    version: Literal['3.8'] = '3.8'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and summon
        """
        return super().get_actions(match) + [
            self.create_summon('Lightfall Sword', { 'version': self.version })
        ]


# Talents


class WellspringOfWarLust_3_5(SkillTalent):
    name: Literal['Wellspring of War-Lust']
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Eula'] = 'Eula'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: Literal['Glacial Illumination'] = 'Glacial Illumination'


# charactor base


class Eula_3_8(CharactorBase):
    name: Literal['Eula']
    version: Literal['3.8'] = '3.8'
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        FavoniusBladeworkEdel | IcetideVortex | GlacialIllumination
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            FavoniusBladeworkEdel(),
            IcetideVortex(),
            GlacialIllumination()
        ]


register_class(Eula_3_8 | WellspringOfWarLust_3_5 | LightfallSword_3_8)
