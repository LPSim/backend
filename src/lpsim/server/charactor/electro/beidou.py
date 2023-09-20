# type: ignore


from typing import Any, List, Literal

from ...modifiable_values import CostValue
from ...event import ReceiveDamageEventArguments, RoundPrepareEventArguments

from ...action import Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    CostLabels, DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.
# Round status, will last for several rounds and disappear
# Skills


class Tidecaller(ElementalSkillBase):
    name: Literal['Tidecaller'] = 'Tidecaller'
    desc: str = (
        'This character gains a Tidecaller: Surf Embrace. '
        'Prepare Skill: Wavestrider.'
    )
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create status
        """
        return [
            self.charge_self(1),
            self.create_charactor_status('Tidecaller: Surf Embrace'),
        ]


class Wavestrider(ElementalSkillBase):
    name: Literal['Wavestrider'] = 'Wavestrider'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        alway invalid to directly use.
        """
        return False

    def get_actions(self, match: Any) -> List[MakeDamageAction]:
        return [
            self.attack_opposite_active(match, self.damage, self.damage_type)
        ]


class Stormbreaker(ElementalBurstBase):
    name: Literal['Stormbreaker'] = 'Stormbreaker'
    desc: str = (
        "Deals _DAMAGE_ Electro DMG, creates 1 Thunderbeast's Targe."
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status("Thunderbeast's Targe"),
        ]


# Talents


class LightningStorm(SkillTalent):
    name: Literal['Lightning Storm']
    desc: str = (
        'Combat Action: When your active character is Beidou, equip this '
        'card. After Beidou equips this card, immediately use Tidecaller '
        'once. When Beidou, who has this card equipped, uses Wavestrider: '
        "If DMG is taken while Prepare Skill is active, Beidou's Normal "
        "Attacks this Round will cost 1 less Unaligned Element. "
        '(Can be triggered 2 times)'
    )
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Beidou'] = 'Beidou'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Tidecaller = Tidecaller()

    usage: int = 2
    max_usage: int = 2
    activated: bool = False

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        reset usage and activate
        """
        self.usage = self.max_usage
        self.activated = False
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self receive damage and has status, activate
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        if not event.final_damage.is_corresponding_charactor_receive_damage(
            self.position, match,
        ):
            # not corresponding charactor
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        for status in charactor.status:
            if status.name == 'Tidecaller: Surf Embrace':
                self.activated = True
                break
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        If activated, decrease self normal attack cost by 1
        """
        if not self.activated:
            # not activated
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR,
        ):
            # not self skill
            return value
        if value.cost.label & CostLabels.NORMAL_ATTACK.value == 0:
            # not normal attack
            return value
        if self.usage <= 0:
            # no usage
            return value
        # decrease
        if value.cost.decrease_cost(None):  # pragma: no branch
            if mode == 'REAL':
                self.usage -= 1
        return value


# charactor base


class Beidou(CharactorBase):
    name: Literal['Beidou']
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Uncrowned Lord of the Ocean" Beidou'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | Tidecaller | Wavestrider | Stormbreaker
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: LightningStorm | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Oceanborne',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Tidecaller(),
            Wavestrider(),
            Stormbreaker(),
        ]
