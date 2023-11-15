from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import SkillEndEventArguments

from ...action import (
    Actions, MakeDamageAction, SwitchCharactorAction
)
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillBase, SkillTalent
)


# Summons


class ShadowswordLoneGale_3_3(AttackerSummonBase):
    name: Literal['Shadowsword: Lone Gale']
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    damage: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If kenki use elemental burst, make damage
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            target_area = ObjectPositionType.SKILL
        ):
            # not our player skill made damage, do nothing
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_BURST:
            # not elemental burst, do nothing
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            event.action.position.charactor_idx]
        if charactor.name != 'Maguu Kenki':
            # not kenki, do nothing
            return []
        target_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target_charactor.position,
                    damage = self.damage,
                    damage_elemental_type = self.damage_elemental_type,
                    cost = Cost(),
                )
            ]
        )]


class ShadowswordGallopingFrost_3_3(ShadowswordLoneGale_3_3):
    name: Literal['Shadowsword: Galloping Frost']
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1


# Skills


class BlusteringBlade(ElementalSkillBase):
    name: Literal['Blustering Blade'] = 'Blustering Blade'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        only create object
        """
        return [
            self.create_summon('Shadowsword: Lone Gale'),
            self.charge_self(1)
        ]


class FrostyAssault(ElementalSkillBase):
    name: Literal['Frosty Assault'] = 'Frosty Assault'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        only create object
        """
        return [
            self.create_summon('Shadowsword: Galloping Frost'),
            self.charge_self(1)
        ]


class PseudoTenguSweeper(ElementalBurstBase):
    name: Literal['Pseudo Tengu Sweeper'] = 'Pseudo Tengu Sweeper'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 3
    )


# Talents


class TranscendentAutomaton_3_3(SkillTalent):
    name: Literal['Transcendent Automaton']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Maguu Kenki'] = 'Maguu Kenki'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
    )
    skill: Literal['Blustering Blade'] = 'Blustering Blade'

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[SwitchCharactorAction]:
        """
        When self use elemental skill, swich to previous or next charactor
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL,
        ):
            # not equipped on charactor, or skill source not self
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill, do nothing
            return []
        table = match.player_tables[self.position.player_idx]
        skill: SkillBase = match.get_object(event.action.position)
        if skill.name == 'Blustering Blade':
            # switch to next charactor
            next_idx = table.next_charactor_idx()
            if next_idx is None:
                # no next charactor, do nothing
                return []
            return [SwitchCharactorAction(
                player_idx = self.position.player_idx,
                charactor_idx = next_idx,
            )]
        elif skill.name == 'Frosty Assault':
            # switch to previous charactor
            prev_idx = table.previous_charactor_idx()
            if prev_idx is None:
                # no next charactor, do nothing
                return []
            return [SwitchCharactorAction(
                player_idx = self.position.player_idx,
                charactor_idx = prev_idx,
            )]
        else:
            raise AssertionError('skill name not match')


# charactor base


class MaguuKenki_3_4(CharactorBase):
    name: Literal['Maguu Kenki']
    version: Literal['3.4'] = '3.4'
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase
        | BlusteringBlade | FrostyAssault | PseudoTenguSweeper
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Ichimonji',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            BlusteringBlade(),
            FrostyAssault(),
            PseudoTenguSweeper()
        ]


register_class(
    MaguuKenki_3_4 | TranscendentAutomaton_3_3 | ShadowswordLoneGale_3_3
    | ShadowswordGallopingFrost_3_3
)
