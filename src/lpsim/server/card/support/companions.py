from typing import Any, Dict, Literal, List

from ....utils.class_registry import register_base_class, register_class

from ...modifiable_values import CombatActionValue, CostValue

from ...dice import Dice

from .base import (
    LimitedEffectSupportBase, RoundEffectSupportBase, SupportBase, 
    UsageWithRoundRestrictionSupportBase
)
from ...consts import (
    ELEMENT_DEFAULT_ORDER, CostLabels, DamageElementalType, DamageType, 
    DieColor, ElementType, ELEMENT_TO_DIE_COLOR, ElementalReactionType, 
    IconType, ObjectPositionType, PlayerActionLabels, SkillType
)
from ...struct import Cost, ObjectPosition
from ...action import (
    Actions, ChangeObjectUsageAction, ChargeAction, CreateDiceAction, 
    DrawCardAction, MoveObjectAction, RemoveDiceAction, RemoveObjectAction
)
from ...event import (
    ActionEndEventArguments, ChangeObjectUsageEventArguments, 
    ChooseCharactorEventArguments, MoveObjectEventArguments, 
    PlayerActionStartEventArguments, 
    ReceiveDamageEventArguments,
    RemoveObjectEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments, 
    SwitchCharactorEventArguments, UseCardEventArguments
)


class CompanionBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.COMPANION.value


register_base_class(CompanionBase)


class RoundEffectCompanionBase(RoundEffectSupportBase, CompanionBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.COMPANION.value


class Paimon_3_3(CompanionBase):
    name: Literal['Paimon']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 3)
    usage: int = 2
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

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


class Katheryne_3_6(RoundEffectCompanionBase):
    name: Literal['Katheryne']
    version: Literal['3.6'] = '3.6'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CombatActionValue:
        """
        Copied from team status Leave It to Me!
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if self.usage <= 0:
            # no usage
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # not self switch charactor, do nothing
            return value
        if value.action_label & PlayerActionLabels.SWITCH.value == 0:
            # not switch charactor, do nothing
            return value
        if not value.do_combat_action:
            # already quick action, do nothing
            return value
        # self switch charactor, change to quick action
        value.do_combat_action = False
        assert mode == 'REAL'
        self.usage -= 1
        return value


class Katheryne_3_3(Katheryne_3_6):
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)


class Timaeus_3_3(CompanionBase, UsageWithRoundRestrictionSupportBase):
    name: Literal['Timaeus']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_one_round: int = 1
    decrease_target: int = CostLabels.ARTIFACT.value
    usage: int = 2
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def play(self, match: Any) -> List[Actions]:
        self.usage = 2
        return []

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round end, increase usage.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        self.usage += 1
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        When in support, and self equip, and usage is enough, and has round
        usage, decrease cost.
        """
        decrease_number = value.cost.total_dice_cost
        if (
            self.position.area != ObjectPositionType.SUPPORT
            or self.position.player_idx != value.position.player_idx
            or value.cost.label & self.decrease_target == 0
            or decrease_number > self.usage
            or decrease_number == 0
            or self.usage_this_round <= 0
        ):
            # not in support, not self player, not target equip, not enough 
            # usage this round or total usage, do nothing
            return value
        # decrease all cost
        for _ in range(decrease_number):
            value.cost.decrease_cost(None)
        if mode == 'REAL':
            self.usage_this_round -= 1
            self.usage -= decrease_number
        return value


class Wagner_3_3(Timaeus_3_3):
    name: Literal['Wagner']
    decrease_target: int = CostLabels.WEAPON.value


class ChefMao_4_1(RoundEffectCompanionBase, LimitedEffectSupportBase):
    name: Literal['Chef Mao']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1
    limited_usage: int = 1

    def _limited_action(self, match: Any) -> List[DrawCardAction]:
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            whitelist_cost_labels = CostLabels.FOOD.value,
            draw_if_filtered_not_enough = False,
        )]

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        """
        When use food card, create one random elemental die and do limited
        action.
        """
        if self.position.area == ObjectPositionType.SUPPORT:
            # on support area, do effect
            if self.usage <= 0:
                # usage is 0, do nothing
                return []
            if (
                event.action.card_position.player_idx 
                != self.position.player_idx
            ):
                # not our charactor use card, do nothing
                return []
            if event.card.cost.label & CostLabels.FOOD.value == 0:
                # not food card, do nothing
                return []
            # our use food card, generate die and do limited action
            self.usage -= 1
            return [CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 1,
                different = True  # use different to avoid generating OMNI
            )] + self.do_limited_action(match)
        # otherwise, do normal response
        return super().event_handler_USE_CARD(event, match)


class ChefMao_3_3(ChefMao_4_1):
    version: Literal['3.3']
    limited_usage: int = 0


class Tubby_3_3(RoundEffectCompanionBase):
    name: Literal['Tubby']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1
    decrease_target: int = CostLabels.LOCATION.value
    decrease_cost: int = 2

    def use(self, mode: Literal['REAL', 'TEST'], result: List[bool]) -> None:
        """
        When used, check whether need to decrease usage.
        """
        if True in result:
            if mode == 'REAL':
                self.usage -= 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        If in support and self use target card, decrease cost by 2.
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
        if value.cost.label & self.decrease_target == 0:
            # not decrease target
            return value
        # decrease
        result = [
            value.cost.decrease_cost(None) for _ in range(self.decrease_cost)
        ]
        self.use(mode, result)
        return value


class Timmie_3_3(CompanionBase):
    name: Literal['Timmie']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def play(self, match: Any) -> List[ChangeObjectUsageAction]:
        """
        When played, first reset usage to 0, then increase usage.
        """
        self.usage = 0
        return [ChangeObjectUsageAction(
            object_position = self.position,
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


class Liben_3_3(CompanionBase):
    name: Literal['Liben']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

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


class ChangTheNinth_3_3(CompanionBase):
    name: Literal['Chang the Ninth']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3
    inspiration_got: bool = False
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

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
        if event.final_damage.damage_type == DamageType.HEAL:
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


class Ellin_3_3(RoundEffectCompanionBase):
    """
    TODO: When draw in the round and play, should also decrease cost.
    """
    name: Literal['Ellin']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 0
    max_usage_per_round: int = 1
    recorded_skill_ids: Dict[int, None] = {}

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.recorded_skill_ids.clear()
        return super().event_handler_ROUND_PREPARE(event, match)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        Record skill id when skill end.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.action.position.player_idx != self.position.player_idx:
            # not self player
            return []
        self.recorded_skill_ids[event.action.position.id] = None
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        When a skill id is recorded, and has usage, decrease cost.
        """
        if (
            self.position.area != ObjectPositionType.SUPPORT
            or self.usage <= 0
            or value.position.id not in self.recorded_skill_ids
            or value.position.player_idx != self.position.player_idx
            or value.cost.label & (
                CostLabels.NORMAL_ATTACK.value
                | CostLabels.ELEMENTAL_SKILL.value
                | CostLabels.ELEMENTAL_BURST.value
            ) == 0
        ):
            # no usage, not self player, not recorded skill id or not skill
            return value
        # decrease
        if value.cost.decrease_cost(value.cost.elemental_dice_color):
            if mode == 'REAL':
                self.usage -= 1
        return value


class IronTongueTian_3_3(CompanionBase):
    name: Literal['Iron Tongue Tian']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    usage: int = 2
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[ChargeAction | RemoveObjectAction]:
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        table = match.player_tables[self.position.player_idx]
        charactors = [table.get_active_charactor()]
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.position.id != charactors[0].position.id:
                charactors.append(c)
        for c in charactors:
            if c.is_alive and c.charge < c.max_charge:
                assert self.usage > 0
                self.usage -= 1
                return [ChargeAction(
                    player_idx = c.position.player_idx,
                    charactor_idx = c.position.charactor_idx,
                    charge = 1,
                )] + self.check_should_remove()
        return []


class LiuSu_3_3(CompanionBase, UsageWithRoundRestrictionSupportBase):
    name: Literal['Liu Su']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 2
    max_usage_one_round: int = 1
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def charge(self, charactor: Any) -> List[ChargeAction 
                                             | RemoveObjectAction]:
        """
        If this charactor is our charactor and has no energy, charge it.
        """
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and charactor.position.player_idx == self.position.player_idx
            and charactor.charge == 0 
            and self.has_usage()
        ):
            # in support, and our charactor, and no energy
            self.use()
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


class Hanachirusato_3_7(CompanionBase):
    name: Literal['Hanachirusato']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3
    decrease_target: int = CostLabels.WEAPON.value | CostLabels.ARTIFACT.value
    decrease_number: int = 2
    effect_triggered: bool = False
    icon_type: Literal[IconType.COUNTER] = IconType.COUNTER

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When any sommon is removed, add one usage
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.action.object_position.area != ObjectPositionType.SUMMON:
            # not summon, do nothing
            return []
        self.usage = min(self.usage + 1, self.max_usage)
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['REAL', 'TEST']
    ) -> CostValue:
        """
        When in support, and self use target card, decrease cost by 2.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if self.usage != self.max_usage:
            # not enough usage
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        if value.cost.label & self.decrease_target == 0:
            # not decrease target
            return value
        # decrease
        result = [
            value.cost.decrease_cost(None),
            value.cost.decrease_cost(None),
        ]
        if True in result:
            if mode == 'REAL':
                self.effect_triggered = True
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        if self.position.area == ObjectPositionType.SUPPORT:
            # in support, check if effect triggered. If so, remove self.
            if self.effect_triggered:
                return [RemoveObjectAction(
                    object_position = self.position,
                )]
        return super().event_handler_MOVE_OBJECT(event, match)


class KidKujirai_3_7(CompanionBase):
    name: Literal['Kid Kujirai']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost()
    usage: int = 0
    icon_type: Literal[IconType.NONE] = IconType.NONE

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


class Xudong_3_7(Tubby_3_3):
    name: Literal['Xudong']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(any_dice_number = 2)
    decrease_target: int = CostLabels.FOOD.value
    decrease_cost: int = 2


class Dunyarzad_4_1(Tubby_3_3, LimitedEffectSupportBase):
    name: Literal['Dunyarzad']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 1)
    decrease_target: int = CostLabels.COMPANION.value
    decrease_cost: int = 1

    limited_usage: int = 1
    triggered: bool = False

    def _limited_action(self, match: Any) -> List[DrawCardAction]:
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            whitelist_cost_labels = self.decrease_target,
            draw_if_filtered_not_enough = False,
        )]

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        """
        Do limited action to draw a support card if needed
        """
        if self.position.area == ObjectPositionType.SUPPORT:
            # on support area, do effect
            if (
                event.action.card_position.player_idx 
                != self.position.player_idx
            ):
                # not our charactor use card, do nothing
                return []
            if event.card.cost.label & CostLabels.COMPANION.value == 0:
                # not companion card, do nothing
                return []
            # our use companion card, do limited action
            return self.do_limited_action(match)
        # otherwise, do normal response
        return super().event_handler_USE_CARD(event, match)


class Dunyarzad_3_7(Dunyarzad_4_1): 
    version: Literal['3.7']
    limited_usage: int = 0


class Rana_3_7(RoundEffectCompanionBase):
    name: Literal['Rana']
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


class MasterZhang_3_8(RoundEffectCompanionBase):
    name: Literal['Master Zhang']
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
            if (
                charactor.weapon is not None 
                and self.card_cost_label & CostLabels.WEAPON.value > 0
                or charactor.artifact is not None 
                and self.card_cost_label & CostLabels.ARTIFACT.value > 0
                or charactor.talent is not None 
                and self.card_cost_label & CostLabels.TALENT.value > 0
            ):
                decrease_number += 1
        result = []
        for _ in range(decrease_number):
            result.append(value.cost.decrease_cost(None))
        if True in result:
            if mode == 'REAL':
                self.usage -= 1
        return value


class Setaria_4_0(CompanionBase):
    name: Literal['Setaria']
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 3
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

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


class YayoiNanatsuki_4_1(MasterZhang_3_8):
    name: Literal['Yayoi Nanatsuki']
    version: Literal['4.1'] = '4.1'
    card_cost_label: int = CostLabels.ARTIFACT.value


register_class(
    Paimon_3_3 | Katheryne_3_6 | Timaeus_3_3 | Wagner_3_3 | ChefMao_4_1 
    | Tubby_3_3 | Timmie_3_3 | Liben_3_3 | ChangTheNinth_3_3 | Ellin_3_3 
    | IronTongueTian_3_3 | LiuSu_3_3 | Hanachirusato_3_7 | KidKujirai_3_7 
    | Xudong_3_7 | Dunyarzad_4_1 | Rana_3_7 | MasterZhang_3_8 | Setaria_4_0
    | YayoiNanatsuki_4_1 | Dunyarzad_3_7 | Katheryne_3_3 | ChefMao_3_3
)
