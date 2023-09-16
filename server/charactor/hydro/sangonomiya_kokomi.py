from typing import Any, List, Literal

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue

from ...action import ActionTypes, Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class BakeKurage(AttackerSummonBase):
    name: Literal['Bake-Kurage'] = 'Bake-Kurage'
    desc: str = (
        'End Phase: Deal 1 Hydro DMG, heal your active character for 1 HP.'
    )
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        make_damage_action = ret[-1]
        assert make_damage_action.type == ActionTypes.MAKE_DAMAGE
        make_damage_action.damage_value_list.append(DamageValue(
            position = self.position,
            damage_type = DamageType.HEAL,
            target_position = active_charactor.position,
            damage = -1,
            damage_elemental_type = DamageElementalType.HEAL,
            cost = Cost(),
        ))
        # if our Kokomi with talent and Ceremonial Garment, increase damage
        charactors = match.player_tables[self.position.player_idx].charactors
        is_kokomi_talent_status: bool = False
        for c in charactors:
            if (
                c.name == 'Sangonomiya Kokomi'
                and c.talent is not None
            ):
                # our Kokomi with talent
                status_found = False
                for s in c.status:
                    if s.name == 'Ceremonial Garment':
                        # Ceremonial Garment exists
                        status_found = True
                        break
                if status_found:
                    # Ceremonial Garment exists
                    is_kokomi_talent_status = True
                    break
        if is_kokomi_talent_status:
            # increase damage
            make_damage_action.damage_value_list[0].damage += 1
        return ret


# Skills


class KuragesOath(ElementalSkillBase):
    name: Literal["Kurage's Oath"] = "Kurage's Oath"
    desc: str = (
        'This character gains Hydro Application and summons 1 Bake-Kurage.'
    )
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        application and create object
        """
        return [
            self.charge_self(1),
            self.element_application_self(match, DamageElementalType.HYDRO),
            self.create_summon('Bake-Kurage'),
        ]


class NereidsAscension(ElementalBurstBase):
    name: Literal["Nereid's Ascension"] = "Nereid's Ascension"
    desc: str = (
        'Deals 2 Hydro DMG. Heals all allied characters for 1 point. '
        'This character gains Ceremonial Garment.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        damage, heal and create charactor status
        """
        ret = super().get_actions(match)
        action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = []
        )
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if charactor.is_alive:
                action.damage_value_list.append(DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                ))
        ret.append(action)
        ret.append(self.create_charactor_status('Ceremonial Garment'))
        # if has talent, re-create Bake-Kurage
        if self.is_talent_equipped(match):
            ret.append(self.create_summon('Bake-Kurage'))
        return ret


# Talents


class TamakushiCasket(SkillTalent):
    name: Literal['Tamakushi Casket']
    desc: str = (
        'Combat Action: When your active character is Sangonomiya Kokomi, '
        'equip this card. After Sangonomiya Kokomi equips this card, '
        "immediately use Nereid's Ascension once. When your Sangonomiya "
        "Kokomi, who has this card equipped, uses Nereid's Ascension: If "
        "Bake-Kurage is on the field, its Usage(s) will be refreshed. While "
        'Ceremonial Garment exists, Bake-Kurage deals +1 DMG'
    )
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Sangonomiya Kokomi'] = 'Sangonomiya Kokomi'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: NereidsAscension = NereidsAscension()


# charactor base


class SangonomiyaKokomi(CharactorBase):
    name: Literal['Sangonomiya Kokomi']
    version: Literal['3.6'] = '3.6'
    desc: str = '''"Pearl of Wisdom" Sangonomiya Kokomi'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | KuragesOath | NereidsAscension
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: TamakushiCasket | None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'The Shape of Water',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            KuragesOath(),
            NereidsAscension()
        ]
