from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue

from ...action import (
    ActionTypes, Actions, ChangeObjectUsageAction, MakeDamageAction
)
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class BakeKurage_3_5(AttackerSummonBase):
    name: Literal['Bake-Kurage'] = 'Bake-Kurage'
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        make_damage_action = ret[0]
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
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        summons = match.player_tables[
            self.position.player_idx].summons
        kurage_found = None
        for s in summons:
            if s.name == 'Bake-Kurage':
                kurage_found = s
                break
        talent = charactor.talent
        if talent is not None:
            if talent.version == '3.5':
                # if has 3.5 talent, re-create Bake-Kurage
                if kurage_found:
                    ret.append(self.create_summon('Bake-Kurage'))
            elif talent.version == '4.2':
                # with 4.2 talent
                if kurage_found is not None:
                    # found kurage, increase usage
                    ret.append(
                        ChangeObjectUsageAction(
                            object_position = kurage_found.position,
                            change_usage = 1
                        )
                    )
                else:
                    # otherwise, create kurage with 1 usage
                    ret.append(self.create_summon('Bake-Kurage', {
                        'usage': 1,
                        'max_usage': 1,
                    }))
            else:
                raise NotImplementedError
        return ret


# Talents


class TamakushiCasket_4_2(SkillTalent):
    name: Literal['Tamakushi Casket']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Sangonomiya Kokomi'] = 'Sangonomiya Kokomi'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: Literal["Nereid's Ascension"] = "Nereid's Ascension"


# charactor base


class SangonomiyaKokomi_3_6(CharactorBase):
    name: Literal['Sangonomiya Kokomi']
    version: Literal['3.6'] = '3.6'
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

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'The Shape of Water',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            KuragesOath(),
            NereidsAscension()
        ]


register_class(SangonomiyaKokomi_3_6 | TamakushiCasket_4_2 | BakeKurage_3_5)
