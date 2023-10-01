from typing import Any, List, Literal

from ...action import (
    ActionTypes, CharactorReviveAction, CreateObjectAction, MakeDamageAction
)
from ...struct import Cost, ObjectPosition
from ...modifiable_values import DamageValue
from ...consts import (
    CostLabels, DamageElementalType, DamageType, ObjectPositionType
)
from ...object_base import CardBase


class FoodCardBase(CardBase):
    """
    Base class for food cards.
    """
    cost_label: int = CostLabels.CARD | CostLabels.FOOD
    can_eat_only_if_damaged: bool

    def eat_target(self, match: Any) -> List[int]:
        """
        Get target charactor idxs that can eat.
        """
        ret: List[int] = []
        table = match.player_tables[self.position.player_idx]
        for idx, charactor in enumerate(table.charactors):
            if charactor.is_defeated:
                continue
            is_full = False
            for status in charactor.status:
                if status.name == 'Satiated':
                    is_full = True
                    break
            if is_full:
                continue
            if self.can_eat_only_if_damaged and charactor.damage_taken <= 0:
                continue
            ret.append(idx)
        return ret

    def is_valid(self, match: Any) -> bool:
        """
        If there is at least one target that can eat.
        """
        return len(self.eat_target(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Get targets of this card.
        """
        ret: List[ObjectPosition] = []
        charactors = match.player_tables[self.position.player_idx].charactors
        for idx in self.eat_target(match):
            ret.append(charactors[idx].position)
        return ret

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Add Satiated status to target charactor.
        """
        assert target is not None
        pos = target.set_area(ObjectPositionType.CHARACTOR_STATUS)
        return [CreateObjectAction(
            object_name = 'Satiated',
            object_position = pos,
            object_arguments = {}
        )]


class JueyunGuoba(FoodCardBase):
    name: Literal['Jueyun Guoba']
    desc: str = (
        "During this Round, the target character's next Normal Attack "
        "deals +1 DMG."
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


class AdeptusTemptation(FoodCardBase):
    name: Literal["Adeptus' Temptation"]
    desc: str = (
        "During this Round, the target character's next Elemental Burst "
        "deals +3 DMG."
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


class LotusFlowerCrisp(FoodCardBase):
    name: Literal['Lotus Flower Crisp']
    desc: str = (
        "During this Round, the target character takes -3 DMG the next time."
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


class NorthernSmokedChicken(FoodCardBase):
    name: Literal['Northern Smoked Chicken']
    desc: str = (
        "During this Round, the target character's next Normal Attack cost "
        "less 1 Unaligned Element."
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


class SweetMadame(FoodCardBase):
    name: Literal['Sweet Madame']
    desc: str = '''Heal target character for 1 HP.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = target,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        ))
        return ret


class MondstadtHashBrown(FoodCardBase):
    name: Literal['Mondstadt Hash Brown']
    desc: str = '''Heal target character for 2 HP.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = target,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        ))
        return ret


class MushroomPizza(FoodCardBase):
    name: Literal['Mushroom Pizza']
    desc: str = (
        'Heal target character for 1 HP. For the next two Rounds, heal this '
        'character for 1 HP again at the End Phase.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = target,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        ))
        create_1 = ret[0]
        assert create_1.type == ActionTypes.CREATE_OBJECT
        ret.append(CreateObjectAction(
            object_name = self.name,
            object_position = create_1.object_position,
            object_arguments = {}
        ))
        return ret


class MintyMeatRolls(FoodCardBase):
    name: Literal['Minty Meat Rolls']
    desc: str = (
        "Before this Round ends, the target character's next 3 Normal Attacks "
        "cost 1 less Unaligned Element."
    )
    version: Literal['3.4'] = '3.4'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        action_2.object_arguments['version'] = self.version
        ret.append(action_2)
        return ret


class TeyvatFriedEgg(FoodCardBase):
    name: Literal['Teyvat Fried Egg']
    desc: str = (
        "Revives the target character and heals that character for 1 HP. "
        "(You can only revive 1 character via Food per Round, and a character "
        "can consume at most 1 Food per Round)"
    )
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 2)

    can_eat_only_if_damaged: bool = False

    def is_valid(self, match: Any) -> bool:
        """
        Has target, and not used this round.
        """
        for s in match.player_tables[self.position.player_idx].team_status:
            if s.name == 'Revive on cooldown':
                return False
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Can only target defeated charactors
        """
        return [
            charactor.position for charactor 
            in match.player_tables[self.position.player_idx].charactors 
            if charactor.is_defeated
        ]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | CharactorReviveAction]:
        ret: List[CreateObjectAction | CharactorReviveAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        create_1 = ret[0]
        assert create_1.type == ActionTypes.CREATE_OBJECT
        ret.append(CreateObjectAction(
            object_name = 'Revive on cooldown',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = 0,
            ),
            object_arguments = {}
        ))
        ret = [
            CharactorReviveAction(
                player_idx = target.player_idx,
                charactor_idx = target.charactor_idx,
                revive_hp = 1
            )
        ] + ret
        return ret


class SashimiPlatter(FoodCardBase):
    name: Literal['Sashimi Platter']
    desc: str = (
        "Before this Round ends, the target character's Normal Attacks "
        "deal +1 DMG."
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


class TandooriRoastChicken(FoodCardBase):
    name: Literal['Tandoori Roast Chicken']
    desc: str = (
        "During this Round, all your characters' next Elemental Skills "
        "deal +2 DMG."
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(any_dice_number = 2)

    can_eat_only_if_damaged: bool = False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        As it fulfills all charactors, no need to specify target.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        It will add Tandoori Roast Chicken status to all possible charactors.
        """
        ret: List[CreateObjectAction] = []
        targets = self.eat_target(match)
        assert len(targets) > 0
        charactors = match.player_tables[self.position.player_idx].charactors
        for t in targets:
            charactor = charactors[t]
            pos = charactor.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS)
            ret.append(CreateObjectAction(
                object_name = 'Satiated',
                object_position = pos,
                object_arguments = {}
            ))
            ret.append(CreateObjectAction(
                object_name = self.name,
                object_position = pos,
                object_arguments = {}
            ))
        return ret


class ButterCrab(FoodCardBase):
    name: Literal['Butter Crab']
    desc: str = (
        "During this Round, all your characters take -2 DMG the next time."
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    can_eat_only_if_damaged: bool = False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        As it fulfills all charactors, no need to specify target.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        It will add Butter Crab status to all possible charactors.
        """
        ret: List[CreateObjectAction] = []
        targets = self.eat_target(match)
        assert len(targets) > 0
        charactors = match.player_tables[self.position.player_idx].charactors
        for t in targets:
            charactor = charactors[t]
            pos = charactor.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS)
            ret.append(CreateObjectAction(
                object_name = 'Satiated',
                object_position = pos,
                object_arguments = {}
            ))
            ret.append(CreateObjectAction(
                object_name = self.name,
                object_position = pos,
                object_arguments = {}
            ))
        return ret


FoodCards = (
    JueyunGuoba | AdeptusTemptation | LotusFlowerCrisp | NorthernSmokedChicken
    | SweetMadame | MondstadtHashBrown | MushroomPizza | MintyMeatRolls
    | TeyvatFriedEgg | SashimiPlatter | TandooriRoastChicken | ButterCrab
)
