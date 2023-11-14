from typing import Any, List, Literal

from ....utils.class_registry import register_class


from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import SkillEndEventArguments

from ...action import Actions, CharactorReviveAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class HeraldOfFrost_4_0(AttackerSummonBase):
    name: Literal['Herald of Frost'] = 'Herald of Frost'
    version: Literal['4.0'] = '4.0'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        if event.action.position.player_idx != self.position.player_idx:
            # not our player skill made damage, do nothing
            return []
        assert event.action.position.area == ObjectPositionType.SKILL
        charactors = match.player_tables[self.position.player_idx].charactors
        charactor = charactors[event.action.position.charactor_idx]
        if charactor.name != 'Qiqi':
            # not Qiqi, do nothing
            return []
        if event.action.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack, do nothing
            return []
        # select charactor with most damage taken
        selected_charactor = charactor
        for c in charactors:
            if c.is_alive and c.damage_taken > selected_charactor.damage_taken:
                selected_charactor = c
        # heal charactor
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = selected_charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        )]


# Skills


class AdeptusArtHeraldOfFrost(ElementalSkillBase):
    name: Literal[
        'Adeptus Art: Herald of Frost'] = 'Adeptus Art: Herald of Frost'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [
            self.charge_self(1),
            self.create_summon('Herald of Frost'),
        ]


class AdeptusArtPreserverOfFortune(ElementalBurstBase):
    name: Literal[
        'Adeptus Art: Preserver of Fortune'
    ] = 'Adeptus Art: Preserver of Fortune'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 3
    )

    revive_usage: int = 2

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Make damage and create status. Then if has talent and has revive usage,
        revive all defeated charactors with 2 hp.
        """
        ret = super().get_actions(match) + [
            self.create_team_status('Fortune-Preserving Talisman')
        ]
        if not self.is_talent_equipped(match):
            # no talent
            return ret
        # has talent
        if self.revive_usage <= 0:
            # no revive usage
            return ret
        defeated_charactors: List[CharactorBase] = []
        charactors = match.player_tables[self.position.player_idx].charactors
        for c in charactors:
            if c.is_defeated:
                defeated_charactors.append(c)
        if len(defeated_charactors) == 0:
            # no defeated charactor
            return ret
        # has defeated charactor, revive them
        self.revive_usage -= 1
        for c in defeated_charactors:
            ret.append(CharactorReviveAction(
                player_idx = self.position.player_idx,
                charactor_idx = c.position.charactor_idx,
                revive_hp = 2
            ))
        return ret


# Talents


class RiteOfResurrection_4_0(SkillTalent):
    name: Literal['Rite of Resurrection']
    version: Literal['4.0'] = '4.0'
    charactor_name: Literal['Qiqi'] = 'Qiqi'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 5,
        charge = 3
    )
    skill: Literal[
        'Adeptus Art: Preserver of Fortune'
    ] = 'Adeptus Art: Preserver of Fortune'


# charactor base


class Qiqi_4_0(CharactorBase):
    name: Literal['Qiqi']
    version: Literal['4.0'] = '4.0'
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | AdeptusArtHeraldOfFrost 
        | AdeptusArtPreserverOfFortune
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Ancient Sword Art',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            AdeptusArtHeraldOfFrost(),
            AdeptusArtPreserverOfFortune(),
        ]


register_class(Qiqi_4_0 | RiteOfResurrection_4_0 | HeraldOfFrost_4_0)
