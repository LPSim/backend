from typing import Any, Literal, List

from ...modifiable_values import CostValue

from ...dice import Dice

from .base import RoundEffectSupportBase, SupportBase
from ...consts import (
    ELEMENT_DEFAULT_ORDER, CostLabels, DamageElementalType, DieColor, 
    ElementType, ELEMENT_TO_DIE_COLOR, ElementalReactionType, 
    ObjectPositionType, SkillType
)
from ...struct import Cost, ObjectPosition
from ...action import (
    Actions, ChangeObjectUsageAction, ChargeAction, CreateDiceAction, 
    DrawCardAction, MoveObjectAction, RemoveDiceAction, RemoveObjectAction
)
from ...event import (
    ActionEndEventArguments, ChangeObjectUsageEventArguments, 
    ChooseCharactorEventArguments, PlayerActionStartEventArguments, 
    ReceiveDamageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments, 
    SwitchCharactorEventArguments
)


class CompanionBase(SupportBase):
    cost_label: int = (CostLabels.CARD.value 
                       | CostLabels.COMPANION.value)


class RoundEffectCompanionBase(RoundEffectSupportBase):
    cost_label: int = (CostLabels.CARD.value 
                       | CostLabels.COMPANION.value)


class Paimon(CompanionBase):
    name: Literal['Paimon']
    desc: str = '''When Action Phase begins: Create Omni Element x2.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 3)
    usage: int = 2

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        When in round prepare, increase usage. 
        If usage is 3, remove self, draw a card and create a dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        self.usage -= 1
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 2,
            color = DieColor.OMNI,
        )] + self.check_should_remove()


class Tubby(RoundEffectCompanionBase):
    name: Literal['Tubby']
    desc: str = (
        'When playing a Location Support Card: Spend 2 less Elemental Dice. '
        '(Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        If in support and self use location, decrease cost by 2.
        """
        if self.usage <= 0:
            # no usage
            return value
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        if value.cost.label & CostLabels.LOCATION.value == 0:
            # not location
            return value
        # decrease
        result = [
            value.cost.decrease_cost(None),
            value.cost.decrease_cost(None),
        ]
        if True in result:
            if mode == 'REAL':
                self.usage -= 1
        return value


class Timmie(CompanionBase):
    name: Literal['Timmie']
    desc: str = (
        'Triggers automatically once per Round: This card gains 1 Pigeon. '
        'When this card gains 3 Pigeons, discard this card, then draw 1 card '
        'and create Genius Invokation TCG Omni Dice Omni Element x1.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3

    def play(self, match: Any) -> List[ChangeObjectUsageAction]:
        """
        When played, first reset usage to 0, then increase usage.
        """
        self.usage = 0
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, increase usage. 
        If usage is 3, remove self, draw a card and create a dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Any
    ) -> List[RemoveObjectAction | DrawCardAction | CreateDiceAction]:
        """
        when self usage changed to 3, remove self, draw a card and create a 
        dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.action.object_position.id != self.id:
            # not self
            return []
        ret: List[RemoveObjectAction | DrawCardAction | CreateDiceAction] = []
        if self.usage == 3:
            ret += [
                RemoveObjectAction(
                    object_position = self.position,
                ),
                DrawCardAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    draw_if_filtered_not_enough = True,
                ),
                CreateDiceAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    color = DieColor.OMNI,
                ),
            ]
        return ret


class Liben(CompanionBase):
    name: Literal['Liben']
    desc: str = (
        'End Phase: Collect your unused Elemental Dice (Max 1 of each '
        'Elemental Type). '
        'When Action Phase begins: If this card has collected 3 Elemental '
        'Dice, draw 2 cards and create Omni Element x2, then discard this '
        'card.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3

    def play(self, match: Any) -> List[Actions]:
        self.usage = 0
        return []

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[RemoveDiceAction]:
        """
        Collect different color dice in round end.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        collect_order: List[DieColor] = []
        dice: Dice = match.player_tables[self.position.player_idx].dice
        colors = dice.colors
        # collect die in element default order
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if color in colors:
                collect_order.append(color)
        # collect OMNI at last
        for color in colors:
            if color == DieColor.OMNI:
                collect_order.append(color)
        # only collect dice if usage is not full
        collect_order = collect_order[: self.max_usage - self.usage]
        self.usage += len(collect_order)
        return [RemoveDiceAction(
            player_idx = self.position.player_idx,
            dice_idxs = dice.colors_to_idx(collect_order)
        )]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction | DrawCardAction | RemoveObjectAction]:
        """
        If this card has collected 3 Elemental Dice, draw 2 cards and create 
        Omni Element x2, then discard this card.'
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if self.usage != self.max_usage:
            # not enough dice collected
            return []
        return [ 
            CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 2,
                color = DieColor.OMNI,
            ),
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 2,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position,
            ),
        ]


class ChangTheNinth(CompanionBase):
    name: Literal['Chang the Ninth']
    desc: str = (
        'When either side uses a Skill: If Physical DMG or Piercing DMG was '
        'dealt, or an Elemental Reaction was triggered, this card gains 1 '
        'Inspiration. When this card gains 3 Inspiration, discard this card, '
        'then draw 2 cards.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3
    inspiration_got: bool = False

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[Actions]:
        """
        When anyone start action, reset inspiration got.
        """
        self.inspiration_got = False
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If physical or piercing or elemental reaction, gain inspiration.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.final_damage.damage_type == 'HEAL':
            # heal, do nothing
            return []
        if (
            event.final_damage.damage_elemental_type not in [
                DamageElementalType.PHYSICAL, DamageElementalType.PIERCING]
            and event.final_damage.element_reaction 
            == ElementalReactionType.NONE
        ):
            # not physical piercing and not elemental reaction, do nothing
            return []
        # get inspiration
        self.inspiration_got = True
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        If inspiration got, increase usage. If usage receives max_usage, 
        remove self and draw two cards.
        """
        if self.inspiration_got:
            self.usage += 1
        self.inspiration_got = False
        if self.usage == self.max_usage:
            # remove self and draw two cards
            return [
                RemoveObjectAction(
                    object_position = self.position,
                ),
                DrawCardAction(
                    player_idx = self.position.player_idx,
                    number = 2,
                    draw_if_filtered_not_enough = True
                ),
            ]
        return []


class LiuSu(CompanionBase):
    name: Literal['Liu Su']
    desc: str = (
        'After you switch characters: If the character you switched to does '
        'not have Energy, they will gain 1 Energy. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 2
    used_this_round: bool = False

    def play(self, match: Any) -> List[Actions]:
        self.used_this_round = False
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.used_this_round = False
        return []

    def charge(self, charactor: Any) -> List[ChargeAction 
                                             | RemoveObjectAction]:
        """
        If this charactor is our charactor and has no energy, charge it.
        """
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and charactor.position.player_idx == self.position.player_idx
            and charactor.charge == 0 
            and not self.used_this_round
        ):
            # in support, and our charactor, and no energy
            assert self.usage > 0
            self.usage -= 1
            self.used_this_round = True
            return [ChargeAction(
                player_idx = charactor.position.player_idx,
                charactor_idx = charactor.position.charactor_idx,
                charge = 1,
            )] + self.check_should_remove()
        return []

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[ChargeAction | RemoveObjectAction]:
        charactor = match.player_tables[event.action.player_idx].charactors[
            event.action.charactor_idx]
        return self.charge(charactor)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[ChargeAction | RemoveObjectAction]:
        charactor = match.player_tables[event.action.player_idx].charactors[
            event.action.charactor_idx]
        return self.charge(charactor)


class KidKujirai(CompanionBase):
    name: Literal['Kid Kujirai']
    desc: str = (
        "When the Action Phase begins: Create 1 Omni Element. Then if your "
        "opponent's Support Zone is not full, transfer this card to your "
        "opponent's Support Zone."
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost()
    usage: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction | MoveObjectAction | RemoveObjectAction]:
        """
        Create one OMNI for this side; and if other side has position, move
        to opposite; otherwise remove self.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        ret: List[CreateDiceAction | MoveObjectAction 
                  | RemoveObjectAction] = []
        ret.append(CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 1,
            color = DieColor.OMNI,
        ))
        opposite = match.player_tables[1 - self.position.player_idx].supports
        max_number = match.config.max_support_number
        if len(opposite) >= max_number:
            # opposite side support is full, remove self
            ret.append(RemoveObjectAction(
                object_position = self.position,
            ))
        else:
            # opposite side support is not full, move to opposite
            ret.append(MoveObjectAction(
                object_position = self.position,
                target_position = ObjectPosition(
                    player_idx = 1 - self.position.player_idx,
                    area = ObjectPositionType.SUPPORT,
                    id = self.position.id
                ),
            ))
        return ret


class Rana(RoundEffectCompanionBase):
    name: Literal['Rana']
    desc: str = (
        'After your character uses an Elemental Skill: '
        'Create 1 Elemental Die of the same Type as your next off-field '
        'character. (Once per Round)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        if it is in support are, and self player used a elemental skill,
        and have usage, and have next charactor, generate a die with color 
        of next charactor.
        """
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and event.action.position.player_idx == self.position.player_idx 
            and event.action.skill_type == SkillType.ELEMENTAL_SKILL
            and self.usage > 0
        ):
            table = match.player_tables[self.position.player_idx]
            next_idx = table.next_charactor_idx()
            if next_idx is not None:
                self.usage -= 1
                ele_type: ElementType = table.charactors[next_idx].element
                die_color = ELEMENT_TO_DIE_COLOR[ele_type]
                return [CreateDiceAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    color = die_color,
                )]
        return []


class MasterZhang(RoundEffectCompanionBase):
    name: Literal['Master Zhang']
    desc: str = (
        'When playing a Weapon card: Spend 1 less Elemental Die. On top of '
        'that, for each of your characters already equipped with a Weapon on '
        'the field, you spend 1 less Elemental Die. (Once per Round.)'
    )
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1
    card_cost_label: int = CostLabels.WEAPON.value

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        If has usage, and self use weapon card, decrease.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if self.usage <= 0:
            # no usage
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        if value.cost.label & self.card_cost_label == 0:
            # not corresponding card
            return value
        # decrease
        decrease_number = 1
        table = match.player_tables[self.position.player_idx]
        for charactor in table.charactors:
            if charactor.weapon is not None:
                decrease_number += 1
        result = []
        for _ in range(decrease_number):
            result.append(value.cost.decrease_cost(None))
        if True in result:
            if mode == 'REAL':
                self.usage -= 1
        return value


class Setaria(CompanionBase):
    name: Literal['Setaria']
    desc: str = (
        'After you perform any action, if you have 0 cards in your hand: '
        'Draw 1 card.'
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 3

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Any
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        If self action end and hand is empty, draw card.
        """
        if event.action.position.player_idx != self.position.player_idx:
            # not self player
            return []
        if len(match.player_tables[self.position.player_idx].hands) != 0:
            # not empty hand
            return []
        # draw a card
        self.usage -= 1
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True,
        )] + self.check_should_remove()


Companions = (
    Paimon | Tubby | Timmie | Liben | ChangTheNinth | LiuSu | KidKujirai 
    | Rana | MasterZhang | Setaria
)
