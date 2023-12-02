from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import GameStartEventArguments

from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    CreateStatusPassiveSkill, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class VolatileSporeCloud(ElementalSkillBase):
    name: Literal['Volatile Spore Cloud'] = 'Volatile Spore Cloud'
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )


class FeatherSpreading(ElementalBurstBase):
    name: Literal['Feather Spreading'] = 'Feather Spreading'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Base on usage, increase damage and reset usage
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        found_status: Any = None
        for status in charactor.status:
            if status.name == 'Radical Vitality':  # pragma: no branch
                found_status = status
                break
        else:
            raise AssertionError('Radical Vitality not found')
        if found_status.usage == 0:
            # no usage, do nothing
            return super().get_actions(match)
        # increase damage
        self.damage += found_status.usage
        ret = super().get_actions(match)
        self.damage = 4
        ret.append(ChangeObjectUsageAction(
            object_position = found_status.position,
            change_usage = - found_status.usage
        ))
        return ret


class RadicalVitality(CreateStatusPassiveSkill):
    name: Literal['Radical Vitality'] = 'Radical Vitality'
    status_name: Literal['Radical Vitality'] = 'Radical Vitality'


# Talents


class ProliferatingSpores_3_3(SkillTalent):
    name: Literal['Proliferating Spores']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal[
        'Jadeplume Terrorshroom'] = 'Jadeplume Terrorshroom'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )
    skill: Literal['Volatile Spore Cloud'] = 'Volatile Spore Cloud'

    def equip(self, match: Any) -> List[CreateObjectAction]:
        """
        When equip, re-create Radical Vitality with 1 more max usage
        """
        return [
            CreateObjectAction(
                object_name = 'Radical Vitality',
                object_position = self.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS
                ),
                object_arguments = { 'max_usage': 4 }
            )
        ]


# charactor base


class JadeplumeTerrorshroom_3_3(CharactorBase):
    name: Literal['Jadeplume Terrorshroom']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | VolatileSporeCloud | FeatherSpreading 
        | RadicalVitality
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Majestic Dance',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            VolatileSporeCloud(),
            FeatherSpreading(),
            RadicalVitality()
        ]


register_class(JadeplumeTerrorshroom_3_3 | ProliferatingSpores_3_3)
