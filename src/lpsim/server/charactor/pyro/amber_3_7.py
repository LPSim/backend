from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DefendSummonBase

from ...modifiable_values import DamageValue

from ...action import Actions, MakeDamageAction, RemoveObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    AOESkillBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class BaronBunny_3_7(DefendSummonBase):
    name: Literal['Baron Bunny'] = 'Baron Bunny'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 2
    attack_until_run_out_of_usage: bool = True


# Skills


class Sharpshooter(PhysicalNormalAttackBase):
    name: Literal['Sharpshooter'] = 'Sharpshooter'
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.PYRO)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If has talent, and Baron Bunny in area, do extra 3 pyro damage and 
        remove Baron Bunny.
        """
        ret = super().get_actions(match)
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent = charactor.talent
        if talent is not None:
            summons = match.player_tables[self.position.player_idx].summons
            for summon in summons:
                if summon.name == 'Baron Bunny':
                    target = match.player_tables[
                        1 - self.position.player_idx].get_active_charactor()
                    ret.append(MakeDamageAction(
                        damage_value_list = [
                            DamageValue(
                                position = summon.position,
                                damage_type = DamageType.DAMAGE,
                                target_position = target.position,
                                damage = talent.damage,
                                damage_elemental_type
                                = DamageElementalType.PYRO,
                                cost = Cost(),
                            )
                        ]
                    ))
                    ret.append(RemoveObjectAction(
                        object_position = summon.position
                    ))
                    return ret
        return ret


class ExplosivePuppet(ElementalSkillBase):
    name: Literal['Explosive Puppet'] = 'Explosive Puppet'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object only
        """
        return [
            self.charge_self(1),
            self.create_summon('Baron Bunny'),
        ]


class FieryRain(ElementalBurstBase, AOESkillBase):
    name: Literal['Fiery Rain'] = 'Fiery Rain'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    back_damage: int = 2
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )


# Talents


class BunnyTriggered_4_2(SkillTalent):
    name: Literal['Bunny Triggered']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Amber'] = 'Amber'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )
    skill: Literal['Explosive Puppet'] = 'Explosive Puppet'
    damage: int = 4


class BunnyTriggered_3_7(SkillTalent):
    name: Literal['Bunny Triggered']
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Amber'] = 'Amber'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )
    skill: Literal['Explosive Puppet'] = 'Explosive Puppet'
    damage: int = 3
# charactor base


class Amber_3_7(CharactorBase):
    name: Literal['Amber']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        Sharpshooter | ExplosivePuppet | FieryRain
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            Sharpshooter(),
            ExplosivePuppet(),
            FieryRain()
        ]


register_class(
    Amber_3_7 | BunnyTriggered_3_7 | BunnyTriggered_4_2 | BaronBunny_3_7
)
