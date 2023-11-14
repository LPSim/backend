from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import DeclareRoundEndAttackSummonBase

from ...action import Actions, RemoveObjectAction
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class SesshouSakura_3_7(DeclareRoundEndAttackSummonBase):
    name: Literal['Sesshou Sakura'] = 'Sesshou Sakura'
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 6
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1
    renew_type: Literal['ADD'] = 'ADD'
    extra_attack_usage: int = 4


# Skills


class YakanEvocationSesshouSakura(ElementalSkillBase):
    name: Literal[
        'Yakan Evocation: Sesshou Sakura'] = 'Yakan Evocation: Sesshou Sakura'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [
            self.charge_self(1),
            self.create_summon('Sesshou Sakura'),
        ]


class GreatSecretArtTenkoKenshin(ElementalBurstBase):
    name: Literal[
        'Great Secret Art: Tenko Kenshin'] = 'Great Secret Art: Tenko Kenshin'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        summons = match.player_tables[self.position.player_idx].summons
        sakura: SesshouSakura_3_7 | None = None
        for summon in summons:
            if summon.name == 'Sesshou Sakura':
                sakura = summon
                break
        if sakura is not None:
            # destroy and add status
            ret.append(RemoveObjectAction(object_position = sakura.position))
            ret.append(self.create_team_status('Tenko Thunderbolts'))
            if self.is_talent_equipped(match):
                # add status
                ret.append(self.create_charactor_status(
                    "The Shrine's Sacred Shade"))
        return ret


# Talents


class TheShrinesSacredShade_3_7(SkillTalent):
    name: Literal["The Shrine's Sacred Shade"] = "The Shrine's Sacred Shade"
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Yae Miko'] = 'Yae Miko'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: Literal[
        'Great Secret Art: Tenko Kenshin'
    ] = 'Great Secret Art: Tenko Kenshin'


# charactor base


class YaeMiko_3_7(CharactorBase):
    name: Literal['Yae Miko']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | YakanEvocationSesshouSakura
        | GreatSecretArtTenkoKenshin
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Spiritfox Sin-Eater',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            YakanEvocationSesshouSakura(),
            GreatSecretArtTenkoKenshin(),
        ]


register_class(YaeMiko_3_7 | TheShrinesSacredShade_3_7 | SesshouSakura_3_7)
