"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal, Tuple

from ...event import (
    CharactorDefeatedEventArguments, RoundPrepareEventArguments
)

from ...consts import (
    DieColor, ObjectPositionType, ObjectType, PlayerActionLabels, SkillType
)

from ...object_base import CardBase, MultiTargetCardBase
from ...action import (
    Actions, ChangeObjectUsageAction, ChargeAction, 
    CreateDiceAction, CreateObjectAction, DrawCardAction, 
    GenerateRerollDiceRequestAction, MoveObjectAction, RemoveObjectAction, 
    SkillEndAction, SwitchCharactorAction, UseSkillAction
)
from ...struct import Cost, MultipleObjectPosition, ObjectPosition


class TheBestestTravelCompanion(CardBase):
    name: Literal['The Bestest Travel Companion!']
    desc: str = '''Convert the Elemental Dice spent to Omni Element x2.'''
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


class ChangingShifts(CardBase):
    name: Literal['Changing Shifts']
    desc: str = (
        'The next time you perform "Switch Character": '
        'Spend 1 less Elemental Die.'
    )
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


class TossUp(CardBase):
    name: Literal['Toss-Up']
    desc: str = '''Select any Elemental Dice to reroll. Can reroll 2 times.'''
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


class Strategize(CardBase):
    name: Literal['Strategize']
    desc: str = '''Draw 2 cards.'''
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


class IHaventLostYet(CardBase):
    name: Literal["I Haven't Lost Yet!"]
    desc: str = (
        "Only playable if one of your characters is defeated this Round: "
        "Create Omni Element x1 and your current active character gains 1 "
        "Energy. "
        "(Only one copy of I Haven't Lost Yet! can be played each round.)"
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost()

    activated: bool = False

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


class LeaveItToMe(CardBase):
    name: Literal['Leave It to Me!']
    desc: str = (
        'The next time you perform "Switch Character": '
        'The switch will be considered a Fast Action instead of a '
        'Combat Action.'
    )
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


class WhenTheCraneReturned(CardBase):
    name: Literal['When the Crane Returned']
    desc: str = (
        'The next time you use a Skill: Switch your next character in to be '
        'the active character.'
    )
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


class Starsigns(CardBase):
    name: Literal['Starsigns']
    desc: str = '''Your current Active Character gains 1 Energy.'''
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


class ClaxsArts(CardBase):
    name: Literal["Clax's Arts"]
    desc: str = (
        'Shift 1 Energy from at most 2 of your characters on standby to '
        'your active character.'
    )
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


class MasterOfWeaponry(MultiTargetCardBase):
    name: Literal['Master of Weaponry']
    desc: str = (
        'Shift 1 Weapon Equipment Card that has been equipped to one of your '
        'characters to another one of your characters of the same Weapon '
        'Type, and reset the "usages per Round" limit on its effects.'
    )
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


class BlessingOfTheDivineRelicsInstallation(MasterOfWeaponry):
    name: Literal["Blessing of the Divine Relic's Installation"]
    desc: str = (
        'Shift 1 Artifact Equipment Card that has been equipped to one of '
        'your characters to another one of your characters, '
        'and reset the "usages per Round" limit on its effects.'
    )
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost()
    move_type: Literal[
        ObjectType.WEAPON, ObjectType.ARTIFACT
    ] = ObjectType.ARTIFACT
    reset_usage: bool = True


class QuickKnit(CardBase):
    name: Literal['Quick Knit']
    desc: str = '''Choose one Summon on your side and grant it +1 Usage(s).'''
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
            change_type = 'DELTA',
            change_usage = 1
        )]


class SendOff(CardBase):
    name: Literal['Send Off']
    desc: str = (
        'Choose one Summon on the opposing side and cause it to lose '
        '2 Usage(s).'
    )
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
            change_type = 'DELTA',
            change_usage = -2
        )]


class GuardiansOath(CardBase):
    name: Literal["Guardian's Oath"]
    desc: str = (
        'Destroy all Summons. (Affects both you and your opponent.)'
    )
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


class PlungingStrike(CardBase):
    name: Literal['Plunging Strike']
    desc: str = (
        'Combat Action: Switch to the target character. '
        'That character then uses a Normal Attack.'
    )
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


class HeavyStrike(CardBase):
    name: Literal['Heavy Strike']
    desc: str = (
        "During this round, your current active character's next "
        'Normal Attack deals +1 DMG. '
        'When this Normal Attack is a Charged Attack: Deal +1 additional DMG.'
    )
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


class TheLegendOfVennessa(CardBase):
    name: Literal['The Legend of Vennessa']
    desc: str = '''Create 4 basic Elemental Dice of different types.'''
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


class FriendshipEternal(CardBase):
    name: Literal['Friendship Eternal']
    desc: str = (
        'Players with less than 4 cards in their hand draw cards until their '
        'hand has 4 cards in it.'
    )
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


class RhythmOfTheGreatDream(CardBase):
    name: Literal['Rhythm of the Great Dream']
    desc: str = (
        'The next time you play a Weapon or Artifact from your hand: Spend 1 '
        'less Elemental Die.'
    )
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


class WhereIstheUnseenRazor(CardBase):
    name: Literal['Where Is the Unseen Razor?'] = 'Where Is the Unseen Razor?'
    desc: str = (
        'Return a Weapon card equipped by your character to your Hand. '
        'During this Round, the next time you play a Weapon card: '
        'Spend 2 less Elemental Dice.'
    )
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


class Pankration(CardBase):
    name: Literal['Pankration!']
    desc: str = (
        'Can only be played when you have at least 8 Elemental Dice '
        'remaining, and your opponent has not yet ended their Round: After a '
        'player announces the end of their Round first, the other player, who '
        'has yet to announce the end of their Round, draws 2 cards.'
    )
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


OtherEventCards = (
    TheBestestTravelCompanion | ChangingShifts | TossUp | Strategize
    | IHaventLostYet | LeaveItToMe | WhenTheCraneReturned | Starsigns 
    | ClaxsArts | MasterOfWeaponry | BlessingOfTheDivineRelicsInstallation 
    | QuickKnit | SendOff | GuardiansOath | PlungingStrike | HeavyStrike 
    | TheLegendOfVennessa | FriendshipEternal | RhythmOfTheGreatDream 
    | WhereIstheUnseenRazor | Pankration
)
