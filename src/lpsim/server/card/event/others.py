"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal, Tuple

from ....utils.class_registry import register_class

from ...event import (
    CharactorDefeatedEventArguments, RoundPrepareEventArguments
)

from ...consts import (
    DieColor, ObjectPositionType, ObjectType, PlayerActionLabels, SkillType
)

from ...object_base import EventCardBase, MultiTargetEventCardBase
from ...action import (
    ActionTypes, Actions, ChangeObjectUsageAction, ChargeAction, 
    CreateDiceAction, CreateObjectAction, DrawCardAction, 
    GenerateRerollDiceRequestAction, MoveObjectAction, RemoveObjectAction, 
    SkillEndAction, SwitchCharactorAction, UseSkillAction
)
from ...struct import Cost, MultipleObjectPosition, ObjectPosition


class TheBestestTravelCompanion_3_3(EventCardBase):
    name: Literal['The Bestest Travel Companion!']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        any_dice_number = 2
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateDiceAction]:
        """
        Act the card. Convert the Elemental Dice spent to Omni Element x2.
        """
        assert target is None  # no targets
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            color = DieColor.OMNI,
            number = 2,
        )]


class ChangingShifts_3_3(EventCardBase):
    name: Literal['Changing Shifts']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        When only one charactor is alive, cannot use this card.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        counter = 0
        for charactor in charactors:
            if charactor.is_alive:
                counter += 1
        return counter > 1

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is None  # no targets
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class TossUp_3_3(EventCardBase):
    name: Literal['Toss-Up']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[GenerateRerollDiceRequestAction]:
        assert target is None
        return [GenerateRerollDiceRequestAction(
            player_idx = self.position.player_idx,
            reroll_times = 2,
        )]


class Strategize_3_3(EventCardBase):
    name: Literal['Strategize']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        same_dice_number = 1
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[DrawCardAction]:
        """
        Act the card. Draw two cards.
        """
        assert target is None  # no targets
        return [DrawCardAction(
            player_idx = self.position.player_idx, 
            number = 2,
            draw_if_filtered_not_enough = True
        )]


class IHaventLostYet_4_0(EventCardBase):
    name: Literal["I Haven't Lost Yet!"]
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost()

    activated: bool = False

    available_handler_in_deck: List[ActionTypes] = [
        ActionTypes.CHARACTOR_DEFEATED, 
        ActionTypes.ROUND_PREPARE
    ]

    def is_valid(self, match: Any) -> bool:
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if status.name == self.name:
                # activated in this round
                return False
        return self.activated

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction | CreateDiceAction | CreateObjectAction]:
        """
        1 omni die, 1 energy, and generate used status.
        """
        assert target is None
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = DieColor.OMNI,
                number = 1,
            ),
            ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = match.player_tables[
                    self.position.player_idx].active_charactor_idx,
                charge = 1
            ),
            CreateObjectAction(
                object_name = self.name,
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {}
            )
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset activated.
        """
        self.activated = False
        return []

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        """
        Mark activated.
        """
        if self.position.player_idx != event.action.player_idx:
            return []
        self.activated = True
        return []


class IHaventLostYet_3_3(IHaventLostYet_4_0):
    name: Literal["I Haven't Lost Yet!"]
    version: Literal['3.3']
    cost: Cost = Cost()

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction | CreateDiceAction | CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert ret[-1].type == ActionTypes.CREATE_OBJECT
        # old version not adding team status
        ret = ret[:-1]
        return ret


class LeaveItToMe_3_3(EventCardBase):
    name: Literal['Leave It to Me!']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        """
        When only one charactor is alive, cannot use this card.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        counter = 0
        for charactor in charactors:
            if charactor.is_alive:
                counter += 1
        return counter > 1

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is None  # no targets
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class WhenTheCraneReturned_3_3(EventCardBase):
    name: Literal['When the Crane Returned']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    def is_valid(self, match: Any) -> bool:
        """
        When only one charactor is alive, cannot use this card.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        counter = 0
        for charactor in charactors:
            if charactor.is_alive:
                counter += 1
        return counter > 1

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is None  # no targets
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class Starsigns_3_3(EventCardBase):
    name: Literal['Starsigns']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)

    def is_valid(self, match: Any) -> bool:
        """
        can use if charge not full
        """
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return active_charactor.charge < active_charactor.max_charge

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # active charactor
        return [match.player_tables[
            self.position.player_idx].get_active_charactor().position]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction]:
        assert target is not None
        return [ChargeAction(
            player_idx = target.player_idx,
            charactor_idx = target.charactor_idx,
            charge = 1,
        )]


class ClaxsArts_3_3(EventCardBase):
    name: Literal["Calx's Arts"]
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    def _get_charge_source_and_targets(
            self, match: Any) -> Tuple[int, List[int]]:
        """
        Get charge source and targets.
        """
        table = match.player_tables[self.position.player_idx]
        source = table.active_charactor_idx
        assert source >= 0 and source < len(table.charactors)
        targets = []
        for idx, charactor in enumerate(table.charactors):
            if idx != source and charactor.charge > 0:
                targets.append(idx)
        if len(targets) > 2:
            targets = targets[:2]
        return source, targets

    def is_valid(self, match: Any) -> bool:
        source, targets = self._get_charge_source_and_targets(match)
        return len(targets) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction]:
        assert target is None
        source, targets = self._get_charge_source_and_targets(match)
        assert len(targets) > 0
        ret: List[ChargeAction] = []
        ret.append(ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = source,
            charge = len(targets),
        ))
        for t in targets:
            ret.append(ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = t,
                charge = -1,
            ))
        return ret


class MasterOfWeaponry_4_1(MultiTargetEventCardBase):
    name: Literal['Master of Weaponry']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost()
    move_type: Literal[
        ObjectType.WEAPON, ObjectType.ARTIFACT
    ] = ObjectType.WEAPON
    reset_usage: bool = True

    def _move_target_id(self, charactor: Any) -> int | None:
        """
        If has target, return target id. otherwise return None
        """
        if self.move_type == ObjectType.WEAPON:
            return None if charactor.weapon is None else charactor.weapon.id
        elif self.move_type == ObjectType.ARTIFACT:
            return (
                None if charactor.artifact is None 
                else charactor.artifact.id
            )
        else:
            raise AssertionError('Unknown move type')

    def get_targets(self, match: Any) -> List[MultipleObjectPosition]:
        charactors = match.player_tables[self.position.player_idx].charactors
        ret: List[MultipleObjectPosition] = []
        for charactor in charactors:
            target_id = self._move_target_id(charactor)
            if target_id is not None:
                for target in charactors:
                    if target.id != charactor.id:
                        if (
                            self.move_type == ObjectType.WEAPON
                            and charactor.weapon_type != target.weapon_type
                        ):
                            # weapon type not right
                            continue
                        ret.append(MultipleObjectPosition(
                            positions = [
                                charactor.position.set_id(target_id),
                                target.position.set_id(target_id)
                            ]
                        ))
        return ret

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: MultipleObjectPosition | None, match: Any
    ) -> List[RemoveObjectAction | MoveObjectAction]:
        assert target is not None
        assert len(target.positions) == 2
        ret: List[RemoveObjectAction | MoveObjectAction] = []
        target_charactor = match.player_tables[target.positions[
            1].player_idx].charactors[target.positions[1].charactor_idx]
        target_equip: Any = None
        if self.move_type == ObjectType.WEAPON:
            target_equip = target_charactor.weapon
        elif self.move_type == ObjectType.ARTIFACT:
            target_equip = target_charactor.artifact
        else:
            raise AssertionError('Unknown move type')
        if target_equip is not None:
            ret.append(RemoveObjectAction(
                object_position = target_equip.position
            ))
        return ret + [MoveObjectAction(
            object_position = target.positions[0],
            target_position = target.positions[1],
            reset_usage = self.reset_usage,
        )]


class BlessingOfTheDivineRelicsInstallation_4_1(MasterOfWeaponry_4_1):
    name: Literal["Blessing of the Divine Relic's Installation"]
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost()
    move_type: Literal[
        ObjectType.WEAPON, ObjectType.ARTIFACT
    ] = ObjectType.ARTIFACT
    reset_usage: bool = True


class MasterOfWeaponry_3_3(MasterOfWeaponry_4_1):
    version: Literal['3.3']
    reset_usage: bool = False


class BlessingOfTheDivineRelicsInstallation_3_3(
    BlessingOfTheDivineRelicsInstallation_4_1
):
    version: Literal['3.3']
    reset_usage: bool = False


class QuickKnit_3_3(EventCardBase):
    name: Literal['Quick Knit']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # all current summons
        return [x.position for x in match.player_tables[
            self.position.player_idx].summons]

    def is_valid(self, match: Any) -> bool:
        # should have summon
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        Add 1 usage of selected summon
        """
        assert target is not None
        return [ChangeObjectUsageAction(
            object_position = target,
            change_usage = 1
        )]


class SendOff_3_7(EventCardBase):
    name: Literal['Send Off']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Opposing summons
        """
        summons = match.player_tables[1 - self.position.player_idx].summons
        return [x.position for x in summons]

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        Act the card. Create team status.
        """
        assert target is not None
        return [ChangeObjectUsageAction(
            object_position = target,
            change_usage = -2
        )]


class SendOff_3_3(SendOff_3_7):
    name: Literal['Send Off']
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[RemoveObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is not None
        return [RemoveObjectAction(
            object_position = target,
        )]


class GuardiansOath_3_3(EventCardBase):
    name: Literal["Guardian's Oath"]
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 4)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def is_valid(self, match: Any) -> bool:
        return (
            len(match.player_tables[0].summons) > 0
            or len(match.player_tables[1].summons) > 0
        )

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[RemoveObjectAction]:
        """
        Act the card. Destroy all summons.
        """
        assert target is None
        ret: List[RemoveObjectAction] = []
        for table in match.player_tables:
            for summon in table.summons:
                ret.append(RemoveObjectAction(
                    object_position = summon.position
                ))
        return ret


class PlungingStrike_3_7(EventCardBase):
    name: Literal['Plunging Strike']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 3)

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        return (
            PlayerActionLabels.SWITCH.value
            | PlayerActionLabels.CARD.value
            | PlayerActionLabels.SKILL.value,
            True
        )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        """
        pos: List[ObjectPosition] = []
        table = match.player_tables[self.position.player_idx]
        for cid, charactor in enumerate(table.charactors):
            if charactor.is_alive and cid != table.active_charactor_idx:
                pos.append(charactor.position)
        return pos

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[SwitchCharactorAction | UseSkillAction | SkillEndAction]:
        """
        Switch to target, and use target's normal attack
        """
        assert target is not None
        skills = match.player_tables[target.player_idx].charactors[
            target.charactor_idx].skills
        normal_idx: int = -1
        for idx, skill in enumerate(skills):
            if skill.skill_type == SkillType.NORMAL_ATTACK:
                assert normal_idx == -1, 'Multiple normal attack skill'
                normal_idx = idx
        return [
            SwitchCharactorAction(
                player_idx = target.player_idx,
                charactor_idx = target.charactor_idx
            ),
            UseSkillAction(
                skill_position = skills[normal_idx].position,
            ),
            SkillEndAction(
                position = skills[normal_idx].position,
                target_position = match.player_tables[
                    1 - target.player_idx].get_active_charactor().position,
                skill_type = SkillType.NORMAL_ATTACK
            )
        ]


class HeavyStrike_3_7(EventCardBase):
    name: Literal['Heavy Strike']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # active charactor
        return [match.player_tables[
            self.position.player_idx].get_active_charactor().position]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create charactor status.
        """
        assert target is not None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = target.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = {}
        )]


class TheLegendOfVennessa_3_7(EventCardBase):
    name: Literal['The Legend of Vennessa']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 3)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateDiceAction]:
        """
        Act the card. Create 4 basic Elemental Dice of different types.
        """
        assert target is None
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 4,
                different = True
            ),
        ]


class FriendshipEternal_3_7(EventCardBase):
    name: Literal['Friendship Eternal']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(
        same_dice_number = 2
    )

    def is_valid(self, match: Any) -> bool:
        # if both player have 4 or more cards, cannot use this card.
        for pidx, table in enumerate(match.player_tables):
            if len(table.hands) < 4:
                return True
            if len(table.hands) == 4 and pidx == self.position.player_idx:
                # for self, 4 card can use to draw one card
                return True
        return False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[DrawCardAction]:
        """
        Act the card. Both player draw card until card number reach 4.
        """
        assert target is None  # no targets
        ret: List[DrawCardAction] = []
        for pidx, table in enumerate(match.player_tables):
            target_number = 4
            if len(table.hands) >= target_number:
                # already have enough cards, do nothing
                continue
            ret.append(DrawCardAction(
                player_idx = pidx,
                number = target_number - len(table.hands),
                draw_if_filtered_not_enough = True
            ))
        return ret


class RhythmOfTheGreatDream_3_8(EventCardBase):
    name: Literal['Rhythm of the Great Dream']
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
        """
        assert target is None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class WhereIstheUnseenRazor_4_0(EventCardBase):
    name: Literal['Where Is the Unseen Razor?'] = 'Where Is the Unseen Razor?'
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Self charactors that have weapon.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        res: List[ObjectPosition] = []
        for charactor in charactors:
            if charactor.weapon is not None:
                res.append(charactor.position)
        return res

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MoveObjectAction | CreateObjectAction]:
        assert target is not None
        charactor = match.get_object(target)
        assert charactor is not None
        assert charactor.weapon is not None
        target_position = charactor.weapon.position.set_area(
            ObjectPositionType.HAND)
        return [
            MoveObjectAction(
                object_position = charactor.weapon.position,
                target_position = target_position
            ),
            CreateObjectAction(
                object_name = self.name,
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {}
            )
        ]


class Pankration_4_1(EventCardBase):
    name: Literal['Pankration!']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        return (
            len(match.player_tables[self.position.player_idx].dice.colors) >= 8
            and not match.player_tables[
                1 - self.position.player_idx].has_round_ended
        )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        create status in our side
        """
        assert target is None
        return [
            CreateObjectAction(
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_name = self.name,
                object_arguments = {}
            )
        ]


class Lyresong_4_2(EventCardBase):
    name: Literal['Lyresong'] = 'Lyresong'
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Self charactors that have artifact.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        res: List[ObjectPosition] = []
        for charactor in charactors:
            if charactor.artifact is not None:
                res.append(charactor.position)
        return res

    def is_valid(self, match: Any) -> bool:
        return len(self.get_targets(match)) > 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MoveObjectAction | CreateObjectAction]:
        assert target is not None
        charactor = match.get_object(target)
        assert charactor is not None
        assert charactor.artifact is not None
        target_position = charactor.artifact.position.set_area(
            ObjectPositionType.HAND)
        return [
            MoveObjectAction(
                object_position = charactor.artifact.position,
                target_position = target_position
            ),
            CreateObjectAction(
                object_name = self.name,
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {}
            )
        ]


register_class(
    TheBestestTravelCompanion_3_3 | ChangingShifts_3_3 | TossUp_3_3 
    | Strategize_3_3 | IHaventLostYet_4_0 | LeaveItToMe_3_3 
    | WhenTheCraneReturned_3_3 | Starsigns_3_3 | ClaxsArts_3_3 
    | MasterOfWeaponry_4_1 | BlessingOfTheDivineRelicsInstallation_4_1 
    | QuickKnit_3_3 | SendOff_3_7 | GuardiansOath_3_3 | PlungingStrike_3_7 
    | HeavyStrike_3_7 | TheLegendOfVennessa_3_7 | FriendshipEternal_3_7 
    | RhythmOfTheGreatDream_3_8 | WhereIstheUnseenRazor_4_0 | Pankration_4_1 
    | Lyresong_4_2 | IHaventLostYet_3_3 | MasterOfWeaponry_3_3
    | BlessingOfTheDivineRelicsInstallation_3_3 | SendOff_3_3
)
