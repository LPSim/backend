from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import AOESummonBase

from ...event import RemoveObjectEventArguments

from ...action import Actions, CreateObjectAction, RemoveObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, CostLabels, DamageElementalType, DieColor, 
    ElementType, FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    CreateStatusPassiveSkill, ElementalBurstBase, ElementalNormalAttackBase, 
    ElementalSkillBase, CharactorBase, TalentBase
)


# Summons


class DarkfireFurnace_3_7(AOESummonBase):
    name: Literal['Darkfire Furnace'] = 'Darkfire Furnace'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 1
    back_damage: int = 1


# Skills


class OminousStar(ElementalBurstBase):
    name: Literal['Ominous Star'] = 'Ominous Star'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Darkfire Furnace'),
        ]


class FieryRebirth(CreateStatusPassiveSkill):
    name: Literal['Fiery Rebirth'] = 'Fiery Rebirth'
    status_name: Literal['Fiery Rebirth'] = 'Fiery Rebirth'
    regenerate_when_revive: bool = False


# Talents


class EmbersRekindled_3_7(TalentBase):
    name: Literal['Embers Rekindled']
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal[
        'Abyss Lector: Fathomless Flames'] = 'Abyss Lector: Fathomless Flames'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2
    )
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value 
        | CostLabels.EQUIPMENT.value
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        ret: List[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.name == 'Abyss Lector: Fathomless Flames':
                ret.append(c.position)
        return ret

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def _attach_status(self, match) -> List[Actions]:
        """
        If self charactor do not have Fiery Rebirth, remove self and attach
        Aegis of Abyssal Flame to charactor.
        """
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        status = charactor.status
        fiery_rebirth_found = False
        for s in status:
            if s.name == 'Fiery Rebirth':
                fiery_rebirth_found = True
                break
        if not fiery_rebirth_found:
            # remove self and attach Aegis of Abyssal Flame to charactor
            return [
                RemoveObjectAction(
                    object_position = self.position,
                ),
                CreateObjectAction(
                    object_position = self.position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS
                    ),
                    object_name = 'Aegis of Abyssal Flame',
                    object_arguments = {}
                ),
            ]
        return []

    def equip(self, match: Any) -> List[Actions]:
        return self._attach_status(match)

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        if self.position.area != ObjectPositionType.CHARACTOR:
            return []
        return self._attach_status(match)


# charactor base


class AbyssLectorFathomlessFlames_3_7(CharactorBase):
    name: Literal['Abyss Lector: Fathomless Flames']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.PYRO
    max_hp: int = 6
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | ElementalSkillBase | OminousStar 
        | FieryRebirth
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Flame of Salvation',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Searing Precept',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalSkillBase.get_cost(self.element),
            ),
            OminousStar(),
            FieryRebirth(),
        ]


register_class(
    AbyssLectorFathomlessFlames_3_7 | DarkfireFurnace_3_7 | EmbersRekindled_3_7
)
