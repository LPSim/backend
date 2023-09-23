from typing import Any, List, Literal, Tuple

from ...summon.base import AttackerSummonBase

from ...event import (
    ChooseCharactorEventArguments, RoundPrepareEventArguments, 
    SwitchCharactorEventArguments
)

from ...action import (
    ActionTypes, Actions, CreateObjectAction, RemoveObjectAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, PlayerActionLabels, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, TalentBase
)


# Summons


class LightningRoseSummon(AttackerSummonBase):
    name: Literal['Lightning Rose'] = 'Lightning Rose'
    version: Literal['4.0'] = '4.0'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 2


# Skills


class LightningTouch(ElementalNormalAttackBase):
    name: Literal['Lightning Touch'] = 'Lightning Touch'
    desc: str = (
        'Deals 1 Electro DMG. '
        'If this Skill is a Charged Attack: Attach Conductive to the '
        "opponent's active character."
    )
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = ElementalNormalAttackBase.get_cost(ElementType.ELECTRO)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Do attack; if charged attack, attach conductive
        """
        ret = super().get_actions(match)
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack
            return ret
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        target_position = damage_action.damage_value_list[0].target_position
        ret.append(CreateObjectAction(
            object_name = 'Conductive',
            object_position = target_position.set_area(
                ObjectPositionType.CHARACTOR_STATUS
            ),
            object_arguments = {}
        ))
        return ret


class VioletArc(ElementalSkillBase):
    name: Literal['Violet Arc'] = 'Violet Arc'
    desc: str = (
        "Deals 2 Electro DMG. If Conductive is not attached to the opponent's "
        'active character, Conductive will be attached.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If Conductive not attached, attach Conductive
        otherwise, increase damage.
        """
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        status = target.status
        conductive = None
        for s in status:
            if s.name == 'Conductive':
                conductive = s
                break
        if conductive is None:
            # no conductive
            return super().get_actions(match) + [
                CreateObjectAction(
                    object_name = 'Conductive',
                    object_position = target.position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS
                    ),
                    object_arguments = {}
                )
            ]
        else:
            # has conductive
            self.damage += conductive.usage
            ret = super().get_actions(match)
            self.damage = 2
            ret = [RemoveObjectAction(
                object_position = conductive.position
            )] + ret
            return ret


class LightningRose(ElementalBurstBase):
    name: Literal['Lightning Rose'] = 'Lightning Rose'
    desc: str = '''Deals 2 Electro DMG, summons 1 Lightning Rose.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon(self.name)
        ]


# Talents


class PulsatingWitch(TalentBase):
    name: Literal['Pulsating Witch']
    desc: str = (
        'After you switch to Lisa, who has this card equipped: Attach '
        'Conductive to the opposing active character. (Once per Round)'
    )
    version: Literal['4.0'] = '4.0'
    charactor_name: Literal['Lisa'] = 'Lisa'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 1
    )
    usage: int = 1

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

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        return (
            PlayerActionLabels.CARD.value | PlayerActionLabels.SKILL.value,
            False
        )

    def _attach_conductive_to_opposite_active(
        self, 
        event: SwitchCharactorEventArguments | ChooseCharactorEventArguments,
        match: Any
    ) -> List[CreateObjectAction]:
        if (
            event.action.player_idx != self.position.player_idx
            or event.action.charactor_idx != self.position.charactor_idx
        ):
            # not to this charactor
            return []
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        return [CreateObjectAction(
            object_name = 'Conductive',
            object_position = target.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS
            ),
            object_arguments = {}
        )]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset usage
        """
        self.usage = 1
        return []

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        return self._attach_conductive_to_opposite_active(event, match)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        return self._attach_conductive_to_opposite_active(event, match)


# charactor base


class Lisa(CharactorBase):
    name: Literal['Lisa']
    version: Literal['4.0'] = '4.0'
    desc: str = '''"Witch of Purple Rose" Lisa'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        LightningTouch | VioletArc | LightningRose
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CATALYST
    talent: PulsatingWitch | None = None

    def _init_skills(self) -> None:
        self.skills = [
            LightningTouch(),
            VioletArc(),
            LightningRose()
        ]
