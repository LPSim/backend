from typing import Any, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageDecreaseValue, DamageValue
from ...event import (
    MakeDamageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments
)

from ...action import Actions, MakeDamageAction, RemoveObjectAction
from ...struct import Cost

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

    def _find_dehya(self, match: Any) -> int:
        """
        Find first alive dehya. If not found, return -1.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        active_idx = match.player_tables[
            self.position.player_idx].active_charactor_idx
        for cidx, charactor in enumerate(charactors):
            if (
                charactor.name == 'Dehya'
                and charactor.is_alive
                and cidx != active_idx
            ):
                return cidx
        return -1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        # reset shield usage
        self.shield_usage = 1
        self.shield_triggered = False
        return []

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageDecreaseValue:
        """
        When has shield usage, and Dehya alive, and active is not Dehya, and
        our active charactor took damage, decrease damage by 1 and mark shield
        triggered.
        """
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match
        ):
            # not corresponding charactor receive damage
            return value
        if self.shield_usage <= 0:
            # out of shield usage
            return value
        dehya_idx = self._find_dehya(match)
        if dehya_idx == -1:
            # not found dehya
            return value
        # decrease damage, usage and mark shield triggered
        assert mode == 'REAL'
        value.damage -= 1
        self.shield_usage -= 1
        self.shield_triggered = True
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If self.shield_triggered, then check whether need to deal 1 piercing
        damage to dehya.
        """
        ret: List[MakeDamageAction | RemoveObjectAction] = []
        if self.shield_triggered:
            self.shield_triggered = False
            dehya_idx = self._find_dehya(match)
            dehya = match.player_tables[
                self.position.player_idx].charactors[dehya_idx]
            if (
                dehya.hp >= 7
                and dehya.is_alive
            ):
                # after shield triggered, dehya has at least 7 hp and alive,
                # make 1 piercing damage to dehya
                ret.append(MakeDamageAction(
                    source_player_idx = self.position.player_idx,
                    target_player_idx = self.position.player_idx,
                    damage_value_list = [
                        DamageValue(
                            position = self.position,
                            target_position = dehya.position,
                            damage = 1,
                            damage_type = DamageType.DAMAGE,
                            damage_elemental_type 
                            = DamageElementalType.PIERCING,
                            cost = Cost(),
                        )
                    ]
                ))
        return ret + super().event_handler_MAKE_DAMAGE(event, match)


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
