from typing import Any, List, Literal

from ...event import CreateObjectEventArguments, GameStartEventArguments
from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Skills


class Prowl(ElementalSkillBase):
    name: Literal['Prowl'] = 'Prowl'
    desc: str = '''Deals 1 Pyro DMG. This character gains Stealth.'''
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
        return super().get_actions(match) + [
            self.create_charactor_status('Stealth')
        ]


class StealthMaster(PassiveSkillBase):
    name: Literal['Stealth Master'] = 'Stealth Master'
    desc: str = (
        '(Passive) When the battle begins, this character gains Stealth.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain stealth
        """
        return [self.create_charactor_status('Stealth')]


# Talents


class PaidinFull(SkillTalent):
    name: Literal['Paid in Full']
    desc: str = (
        'Combat Action: When your active character is Fatui Pyro Agent, '
        'equip this card. After Fatui Pyro Agent equips this card, '
        'immediately use Prowl once. When your Fatui Pyro Agent, who has '
        'this card equipped, creates a Stealth, it will have the following '
        'effect: Starting Usage(s) +1, the Physical DMG the character deals '
        'will be converted to Pyro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Fatui Pyro Agent'] = 'Fatui Pyro Agent'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )
    skill: Prowl = Prowl()

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        When create object, check if it is stealth
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, do nothing
            return []
        if not self.position.check_position_valid(
            event.action.object_position, match, player_idx_same = True,
            charactor_idx_same = True, 
            target_area = ObjectPositionType.CHARACTOR_STATUS
        ):
            # not self create charactor status, do nothing
            return []
        if event.action.object_name != 'Stealth':
            # not stealth, do nothing
            return []
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        status = charactor.status[event.create_idx]
        assert status.name == 'Stealth'
        # add 1 usage
        return [ChangeObjectUsageAction(
            object_position = status.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

# charactor base


class FatuiPyroAgent(CharactorBase):
    name: Literal['Fatui Pyro Agent']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Blade of Settlement" Agent'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Prowl | ElementalBurstBase | StealthMaster
    ] = []
    faction: List[FactionType] = [
        FactionType.FATUI
    ]
    weapon_type: WeaponType = WeaponType.OTHER
    talent: PaidinFull | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Thrust',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Prowl(),
            ElementalBurstBase(
                name = 'Blade Ablaze',
                damage = 5,
                damage_type = DamageElementalType.PYRO,
                cost = ElementalBurstBase.get_cost(self.element, 3, 2),
            ),
            StealthMaster()
        ]
