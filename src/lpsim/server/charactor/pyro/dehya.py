from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageValue
from ...event import (
    CreateObjectEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments
)

from ...action import (
    Actions, CreateObjectAction, MakeDamageAction, RemoveObjectAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class FierySanctumField(AttackerSummonBase):
    name: Literal['Fiery Sanctum Field'] = 'Fiery Sanctum Field'
    desc: str = (
        'End Phase: Deal 1 Pyro DMG. '
        'When this Summon is on the field and Dehya is on standby on your '
        'side, then when your active character takes damage: Decrease DMG '
        'taken by 1, and if Dehya has at least 7 HP, deal 1 Piercing DMG to '
        'her (once per round).'
    )
    version: Literal['4.1'] = '4.1'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 1
    shield_usage: int = 1
    shield_triggered: bool = False

    def _create_status(self, match: Any) -> List[CreateObjectAction]:
        """
        Create status
        """
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = 0,
            ),
            object_arguments = {}
        )]

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When created object is self, and not renew, also create teams status
        """
        if event.create_result == 'RENEW':
            # renew, do nothing
            return []
        if (
            event.action.object_name == self.name
            and self.position.check_position_valid(
                event.action.object_position, match, player_idx_same = True,
                area_same = True
            )
        ):
            # name same, and position same, is self created
            return self._create_status(match)
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        # re-generate status
        self.shield_usage = 1
        self.shield_triggered = False
        return self._create_status(match)

    def _remove(self, match: Any) -> List[RemoveObjectAction]:
        """
        If self should remove, and has generated status, remove together.
        """
        status = match.player_tables[
            self.position.player_idx].team_status
        target_status = None
        for s in status:
            if s.name == self.name:
                target_status = s
                break
        ret: List[RemoveObjectAction] = [RemoveObjectAction(
            object_position = self.position,
        )]
        if target_status is not None:
            ret.append(RemoveObjectAction(
                object_position = target_status.position
            ))
        return ret

# Skills


class MoltenInferno(ElementalSkillBase):
    name: Literal['Molten Inferno'] = 'Molten Inferno'
    desc: str = (
        'Summons Fiery Sanctum Field. If Fiery Sanctum Field already exists, '
        'then first deal 1 Pyro DMG.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        summons = match.player_tables[self.position.player_idx].summons
        summon_name = 'Fiery Sanctum Field'
        summon_exists = False
        for summon in summons:
            if summon.name == summon_name:
                summon_exists = True
                break
        if summon_exists:
            # make damage and create summon
            return super().get_actions(match) + [
                self.create_summon(summon_name),
            ]
        return [
            self.create_summon(summon_name),
            self.charge_self(1)
        ]


class LeonineBite(ElementalBurstBase):
    name: Literal['Leonine Bite'] = 'Leonine Bite'
    desc: str = (
        'Deals 3 Pyro DMG, then performs "Prepare Skill" for Incineration '
        'Drive'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_charactor_status('Incineration Drive'),
        ]


class IncinerationDrive(ElementalBurstBase):
    name: Literal['Incineration Drive'] = 'Incineration Drive'
    desc: str = (
        'Deals 3 Pyro DMG.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        Always invalid for prepare skills
        """
        return False


# Talents


class StalwartAndTrue(SkillTalent):
    name: Literal['Stalwart and True']
    desc: str = (
        'Combat Action: When your active character is Dehya, equip this card. '
        'After Dehya equips this card, immediately use Molten Inferno once. '
        'End Phase: If your Dehya, who has this card equipped, has no more '
        'than 6 HP, heal that character for 2 HP.'
    )
    version: Literal['4.1'] = '4.1'
    charactor_name: Literal['Dehya'] = 'Dehya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
    )
    skill: MoltenInferno = MoltenInferno()

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If equipped, and dehya hp <= 6, heal 2 hp
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.hp <= 6:
            return [MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -2,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = self.cost.copy()
                    )
                ],
            )]
        return []


# charactor base


class Dehya(CharactorBase):
    name: Literal['Dehya']
    version: Literal['4.1'] = '4.1'
    desc: str = '''"Flame-Mane" Dehya'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | MoltenInferno | LeonineBite 
        | IncinerationDrive
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: StalwartAndTrue | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Sandstorm Assault',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            MoltenInferno(),
            LeonineBite(),
            IncinerationDrive(),
        ]
