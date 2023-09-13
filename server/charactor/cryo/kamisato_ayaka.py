from typing import Any, Dict, List, Literal

from ...summon.base import AttackerSummonBase

from ...modifiable_values import CostValue
from ...event import (
    ChooseCharactorEventArguments, GameStartEventArguments, 
    RoundPrepareEventArguments, SwitchCharactorEventArguments
)

from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    CostLabels, DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, TalentBase
)


# Summons


class FrostflakeSekiNoTo(AttackerSummonBase):
    name: Literal['Frostflake Seki no To'] = 'Frostflake Seki no To'
    desc: str = '''End Phase: Deal 2 Cryo DMG.'''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 2


# Skills


class KamisatoArtSoumetsu(ElementalBurstBase):
    name: Literal['Kamisato Art: Soumetsu'] = 'Kamisato Art: Soumetsu'
    desc: str = '''Deals 4 Cryo DMG, summons 1 Frostflake Seki no To.'''
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Frostflake Seki no To')
        ]


class KamisatoArtSenho(PassiveSkillBase):
    name: Literal['Kamisato Art: Senho'] = 'Kamisato Art: Senho'
    desc: str = (
        '(Passive) When switched to be the active character, this character '
        'gains Cryo Elemental Infusion.'
    )

    def infuse(self, match: Any) -> List[CreateObjectAction]:
        args: Dict = { 'mark': 'Kamisato Ayaka' }
        if self.is_talent_equipped(match):
            args['talent_activated'] = True
        return [self.create_charactor_status(
            'Cryo Elemental Infusion', args
        )]

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        if (
            event.action.player_idx != self.position.player_idx
            or event.action.charactor_idx != self.position.charactor_idx
        ):
            # not switch to this charactor
            return []
        return self.infuse(match)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        if (
            event.action.player_idx != self.position.player_idx
            or event.action.charactor_idx != self.position.charactor_idx
        ):
            # not choose this charactor
            return []
        return self.infuse(match)

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        As after choosing charactor in game start will be followed by a
        round preparing, to make infuse in game start, we increase its usage
        by 1 if it exists.
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        for status in charactor.status:
            if (  # pragma: no branch
                status.name == 'Cryo Elemental Infusion'
                and 'mark' in status.__fields__
                and status.mark == 'Kamisato Ayaka'
            ):
                # add one usage to avoid disappear
                return [ChangeObjectUsageAction(
                    object_position = status.position,
                    change_type = 'DELTA',
                    change_usage = 1
                )]
        return []


# Talents


class KantenSenmyouBlessing(TalentBase):
    name: Literal['Kanten Senmyou Blessing']
    desc: str = (
        'The Cryo Elemental Infusion created by your Kamisato Ayaka, who has '
        'this card equipped, allows the character to which it is attached to '
        'deal +1 Cryo DMG. When you switch to Kamisato Ayaka, who has this '
        'card equipped: Spend 1 less Elemental Die. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Kamisato Ayaka'] = 'Kamisato Ayaka'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 2
    )
    usage: int = 1
    max_usage: int = 1

    def is_valid(self, match: Any) -> bool:
        """
        Only corresponding charactor is active charactor can equip this card.
        """
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError('Talent is not in hand')
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        All ayaka are targets
        """
        assert self.position.area != ObjectPositionType.CHARACTOR
        ret: List[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.name == self.charactor_name and c.is_alive:
                ret.append(c.position)
        return ret

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset usage
        """
        self.usage = self.max_usage
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If equipped, and has usage, and switch to ayaka, reduce 1 cost.
        """
        if self.usage <= 0:
            # out of usage, do nothing
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR.value == 0:
            # not switch charactor, do nothing
            return value
        assert value.target_position is not None
        if not self.position.check_position_valid(
            value.target_position, match, player_idx_same = True,
            charactor_idx_same = True, area_same = True,
            source_area = ObjectPositionType.CHARACTOR,
        ):
            # not equipped or not switch to ayaka, do nothing
            return value
        if value.cost.decrease_cost(None):  # pragma: no branch
            # reduce 1 cost
            if mode == 'REAL':
                self.usage -= 1
        return value


# charactor base


class KamisatoAyaka(CharactorBase):
    name: Literal['Kamisato Ayaka']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Frostflake Heron" Kamisato Ayaka'''
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | KamisatoArtSoumetsu
        | KamisatoArtSenho
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: KantenSenmyouBlessing | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Kamisato Art: Kabuki',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Kamisato Art: Hyouka',
                damage_type = DamageElementalType.CRYO,
                cost = ElementalSkillBase.get_cost(self.element)
            ),
            KamisatoArtSoumetsu(),
            KamisatoArtSenho()
        ]
