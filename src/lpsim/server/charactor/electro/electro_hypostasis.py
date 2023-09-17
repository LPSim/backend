from typing import Any, List, Literal, Tuple

from ...summon.base import AttackerSummonBase

from ...modifiable_values import CostValue, DamageValue
from ...event import GameStartEventArguments, RoundPrepareEventArguments

from ...action import (
    Actions, CreateObjectAction, MakeDamageAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    CostLabels, DamageElementalType, DamageType, DieColor, ElementType, 
    FactionType, ObjectPositionType, PlayerActionLabels, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    PassiveSkillBase, CharactorBase, TalentBase
)


# Summons


class ChainsOfWardingThunder(AttackerSummonBase):
    name: Literal['Chains of Warding Thunder'] = 'Chains of Warding Thunder'
    desc: str = (
        'End Phase: Deal 1 Electro DMG. '
        'When this Summon is on the field: Your opponent will have to spend '
        '1 additional Elemental Die when performing "Switch Character." '
        '(Once per Round) Usage(s): 2'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1

    increase_cost_valid: bool = True

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When reaching prepare, reset usage
        """
        self.increase_cost_valid = True
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        When increase_cost_valid, enemy perform charactor switch will increase
        1 cost.
        """
        if not self.increase_cost_valid:
            # out of usage, not modify
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR == 0:
            # not switch charactor, not modify
            return value
        if value.position.player_idx == self.position.player_idx:
            # self switch, not modify
            return value
        # add 1 cost
        value.cost.any_dice_number += 1
        if mode == 'REAL':
            self.increase_cost_valid = False
        return value


# Skills


class RockPaperScissorsCombo(ElementalSkillBase):
    name: Literal['Rock-Paper-Scissors Combo'] = 'Rock-Paper-Scissors Combo'
    desc: str = (
        'Deals 2 Electro DMG and then separately performs "Prepare Skill" for '
        'Rock-Paper-Scissors Combo: Scissors and '
        'Rock-Paper-Scissors Combo: Paper.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 5
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create prepare skill
        """
        return super().get_actions(match) + [
            self.create_charactor_status('Rock-Paper-Scissors Combo: Scissors')
        ]


class RockPaperScissorsComboScissors(ElementalSkillBase):
    name: Literal[
        'Rock-Paper-Scissors Combo: Scissors'
    ] = 'Rock-Paper-Scissors Combo: Scissors'
    desc: str = (
        'Deals 2 Electro DMG and then performs "Prepare Skill" for '
        'Rock-Paper-Scissors Combo: Paper.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        Cannot use by player directly
        """
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create prepare skill
        """
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.create_charactor_status('Rock-Paper-Scissors Combo: Paper')
        ]


class RockPaperScissorsComboPaper(ElementalSkillBase):
    name: Literal[
        'Rock-Paper-Scissors Combo: Paper'
    ] = 'Rock-Paper-Scissors Combo: Paper'
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        Cannot use by player directly
        """
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Do not charge.
        """
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type),
        ]


class LightningLockdown(ElementalBurstBase):
    name: Literal['Lightning Lockdown'] = 'Lightning Lockdown'
    desc: str = '''Deals 2 Electro DMG, summons Chains of Warding Thunder.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_summon('Chains of Warding Thunder')
        ]


class ElectroCrystalCore(PassiveSkillBase):
    name: Literal['Electro Crystal Core'] = 'Electro Crystal Core'
    desc: str = (
        '(Passive) When the battle begins, this character gains '
        'Electro Crystal Core.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain electro crystal core
        """
        return [self.create_charactor_status(self.name)]


# Talents


class AbsorbingPrism(TalentBase):
    name: Literal['Absorbing Prism']
    desc: str = (
        'Combat Action: When your active character is Electro Hypostasis, '
        'heal that character for 3 HP and attach the Electro Crystal Core to '
        'them.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Electro Hypostasis'] = 'Electro Hypostasis'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )
    remove_when_used: bool = True

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        return PlayerActionLabels.CARD.value, True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MakeDamageAction | CreateObjectAction]:
        """
        Using this card will heal electro hypostasis by 3 hp and attach
        electro crystal core to it. No need to equip it.
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        assert charactor.name == self.charactor_name
        return [
            MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -3,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = Cost(),
                    )
                ],
            ),
            CreateObjectAction(
                object_name = 'Electro Crystal Core',
                object_position = charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_arguments = {}
            )
        ]


# charactor base


class ElectroHypostasis(CharactorBase):
    name: Literal['Electro Hypostasis']
    version: Literal['3.7'] = '3.7'
    desc: str = '''Electro Hypostasis'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 8
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | RockPaperScissorsCombo 
        | RockPaperScissorsComboScissors | RockPaperScissorsComboPaper
        | LightningLockdown | ElectroCrystalCore
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER
    talent: None = None

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Electro Crystal Projection',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            RockPaperScissorsCombo(),
            RockPaperScissorsComboScissors(),
            RockPaperScissorsComboPaper(),
            LightningLockdown(),
            ElectroCrystalCore(),
        ]
