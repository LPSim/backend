from typing import Any, List, Literal

from ....utils.class_registry import register_base_class, register_class

from ...action import (
    ActionTypes,
    Actions,
    CharacterReviveAction,
    CreateObjectAction,
    MakeDamageAction,
)
from ...struct import Cost, ObjectPosition
from ...modifiable_values import DamageValue
from ...consts import CostLabels, DamageElementalType, DamageType, ObjectPositionType
from ...object_base import EventCardBase


class FoodCardBase(EventCardBase):
    """
    Base class for food cards.
    """

    cost_label: int = (
        CostLabels.CARD.value | CostLabels.FOOD.value | CostLabels.EVENT.value
    )
    can_eat_only_if_damaged: bool

    def eat_target(self, match: Any) -> List[int]:
        """
        Get target character idxs that can eat.
        """
        ret: List[int] = []
        table = match.player_tables[self.position.player_idx]
        for idx, character in enumerate(table.characters):
            if character.is_defeated:
                continue
            is_full = False
            for status in character.status:
                if status.name == "Satiated":
                    is_full = True
                    break
            if is_full:
                continue
            if self.can_eat_only_if_damaged and character.damage_taken <= 0:
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
        characters = match.player_tables[self.position.player_idx].characters
        for idx in self.eat_target(match):
            ret.append(characters[idx].position)
        return ret

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Add Satiated status to target character.
        """
        assert target is not None
        pos = target.set_area(ObjectPositionType.CHARACTER_STATUS)
        return [
            CreateObjectAction(
                object_name="Satiated", object_position=pos, object_arguments={}
            )
        ]


register_base_class(FoodCardBase)


class AllCharacterFoodCard(FoodCardBase):
    """
    Food card that can be eaten by all characters.
    """

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        As it fulfills all characters, no need to specify target.
        """
        return []

    def get_actions(self, target: ObjectPosition | None, match: Any) -> List[Actions]:
        """
        It will add status to all characters that is not satiated.
        """
        ret: List[Actions] = []
        targets = self.eat_target(match)
        assert len(targets) > 0
        characters = match.player_tables[self.position.player_idx].characters
        for t in targets:
            character = characters[t]
            ret += self.one_character_action(character.position)
        return ret

    def one_character_action(self, pos: ObjectPosition) -> List[Actions]:
        """
        Actions that will be applied to one character. Default is to add
        Satiated and status that has same name as the card.
        """
        ret: List[Actions] = []
        pos = pos.set_area(ObjectPositionType.CHARACTER_STATUS)
        ret.append(
            CreateObjectAction(
                object_name="Satiated", object_position=pos, object_arguments={}
            )
        )
        ret.append(
            CreateObjectAction(
                object_name=self.name, object_position=pos, object_arguments={}
            )
        )
        return ret


class JueyunGuoba_3_3(FoodCardBase):
    name: Literal["Jueyun Guoba"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={},
            )
        )
        return ret


class AdeptusTemptation_3_3(FoodCardBase):
    name: Literal["Adeptus' Temptation"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(any_dice_number=2)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={},
            )
        )
        return ret


class LotusFlowerCrisp_3_3(FoodCardBase):
    name: Literal["Lotus Flower Crisp"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(same_dice_number=1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={},
            )
        )
        return ret


class NorthernSmokedChicken_3_3(FoodCardBase):
    name: Literal["Northern Smoked Chicken"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={},
            )
        )
        return ret


class SweetMadame_3_3(FoodCardBase):
    name: Literal["Sweet Madame"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost()

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=target,
                        damage=-1,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=self.cost.copy(),
                    )
                ],
            )
        )
        return ret


class MondstadtHashBrown_3_3(FoodCardBase):
    name: Literal["Mondstadt Hash Brown"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(same_dice_number=1)

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=target,
                        damage=-2,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=self.cost.copy(),
                    )
                ],
            )
        )
        return ret


class MushroomPizza_3_3(FoodCardBase):
    name: Literal["Mushroom Pizza"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(same_dice_number=1)

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=target,
                        damage=-1,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=self.cost.copy(),
                    )
                ],
            )
        )
        create_1 = ret[0]
        assert create_1.type == ActionTypes.CREATE_OBJECT
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=create_1.object_position,
                object_arguments={},
            )
        )
        return ret


class MintyMeatRolls_3_4(FoodCardBase):
    name: Literal["Minty Meat Rolls"]
    version: Literal["3.4"] = "3.4"
    cost: Cost = Cost(same_dice_number=1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={"version": self.version},
            )
        )
        return ret


class MintyMeatRolls_3_3(MintyMeatRolls_3_4):
    version: Literal["3.3"]


class TeyvatFriedEgg_4_1(FoodCardBase):
    name: Literal["Teyvat Fried Egg"]
    version: Literal["4.1"] = "4.1"
    cost: Cost = Cost(same_dice_number=2)

    can_eat_only_if_damaged: bool = False

    def is_valid(self, match: Any) -> bool:
        """
        Has target, and not used this round.
        """
        for s in match.player_tables[self.position.player_idx].team_status:
            if s.name == "Revive on cooldown":
                return False
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Can only target defeated characters
        """
        return [
            character.position
            for character in match.player_tables[self.position.player_idx].characters
            if character.is_defeated
        ]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | CharacterReviveAction]:
        ret: List[CreateObjectAction | CharacterReviveAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        create_1 = ret[0]
        assert create_1.type == ActionTypes.CREATE_OBJECT
        ret.append(
            CreateObjectAction(
                object_name="Revive on cooldown",
                object_position=ObjectPosition(
                    player_idx=self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        )
        ret = [
            CharacterReviveAction(
                player_idx=target.player_idx,
                character_idx=target.character_idx,
                revive_hp=1,
            )
        ] + ret
        return ret


class TeyvatFriedEgg_3_7(TeyvatFriedEgg_4_1):
    version: Literal["3.7"] = "3.7"
    cost: Cost = Cost(same_dice_number=3)


class SashimiPlatter_3_7(FoodCardBase):
    name: Literal["Sashimi Platter"]
    version: Literal["3.7"] = "3.7"
    cost: Cost = Cost(same_dice_number=1)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=ret[0].object_position,
                object_arguments={},
            )
        )
        return ret


class TandooriRoastChicken_3_7(AllCharacterFoodCard):
    name: Literal["Tandoori Roast Chicken"]
    version: Literal["3.7"] = "3.7"
    cost: Cost = Cost(any_dice_number=2)

    can_eat_only_if_damaged: bool = False


class ButterCrab_3_7(AllCharacterFoodCard):
    name: Literal["Butter Crab"]
    version: Literal["3.7"] = "3.7"
    cost: Cost = Cost(any_dice_number=2)

    can_eat_only_if_damaged: bool = False


register_class(
    JueyunGuoba_3_3
    | AdeptusTemptation_3_3
    | LotusFlowerCrisp_3_3
    | NorthernSmokedChicken_3_3
    | SweetMadame_3_3
    | MondstadtHashBrown_3_3
    | MushroomPizza_3_3
    | MintyMeatRolls_3_4
    | MintyMeatRolls_3_3
    | TeyvatFriedEgg_4_1
    | TeyvatFriedEgg_3_7
    | SashimiPlatter_3_7
    | TandooriRoastChicken_3_7
    | ButterCrab_3_7
)
