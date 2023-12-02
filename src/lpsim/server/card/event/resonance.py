from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import DamageValue

from ...action import (
    ChangeObjectUsageAction, ChargeAction, CreateDiceAction, 
    CreateObjectAction, DrawCardAction, GenerateSwitchCardRequestAction, 
    MakeDamageAction, RemoveDiceAction, SwitchCharactorAction
)
from ...consts import (
    ELEMENT_TO_DIE_COLOR, DamageElementalType, DamageType, DieColor, 
    ElementType, FactionType, ObjectPositionType
)

from ...object_base import EventCardBase
from ...struct import Cost, DeckRestriction, ObjectPosition


class ElementalResonanceCardBase(EventCardBase):
    element: ElementType

    def get_deck_restriction(self) -> DeckRestriction:
        """
        For element resonance cards, should contain at least 2 charactors of
        the corresponding element.
        """
        return DeckRestriction(
            type = 'ELEMENT',
            name = self.element.value,
            number = 2
        )


name_to_element_type = {
    'Elemental Resonance: Woven Flames': ElementType.PYRO,
    'Elemental Resonance: Woven Ice': ElementType.CRYO,
    'Elemental Resonance: Woven Stone': ElementType.GEO,
    'Elemental Resonance: Woven Thunder': ElementType.ELECTRO,
    'Elemental Resonance: Woven Waters': ElementType.HYDRO,
    'Elemental Resonance: Woven Weeds': ElementType.DENDRO,
    'Elemental Resonance: Woven Winds': ElementType.ANEMO,
}


class WovenCards_3_3(ElementalResonanceCardBase):
    name: Literal[
        'Elemental Resonance: Woven Flames', 
        'Elemental Resonance: Woven Ice',
        'Elemental Resonance: Woven Stone', 
        'Elemental Resonance: Woven Thunder',
        'Elemental Resonance: Woven Waters',
        'Elemental Resonance: Woven Weeds',
        'Elemental Resonance: Woven Winds'
    ]
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    element: ElementType = ElementType.NONE  # will update element in __init__

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.element = name_to_element_type[self.name]

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateDiceAction]:
        """
        Create one corresponding element dice
        """
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            color = ELEMENT_TO_DIE_COLOR[self.element],
            number = 1,
        )]


class ShatteringIce_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Shattering Ice']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.CRYO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # avtive character
        return [match.player_tables[
            self.position.player_idx].get_active_charactor().position]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create status
        """
        assert target is not None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = target.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = {}
        )]


class SoothingWater_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Soothing Water']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.HYDRO

    def is_valid(self, match: Any) -> bool:
        """
        At least one charactor is taken damage.
        """
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if charactor.is_alive and charactor.damage_taken > 0:
                return True
        return False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MakeDamageAction]:
        """
        heal active 2, others 1.
        """
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        damage_action = MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = active_charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        )
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if (
                charactor.is_alive
                and charactor.position != active_charactor.position
            ):
                damage_action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -1,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = self.cost.copy()
                    )
                )
        return [damage_action]


class FerventFlames_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Fervent Flames']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.PYRO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # avtive character
        return [match.player_tables[
            self.position.player_idx].get_active_charactor().position]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create status
        """
        assert target is not None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = target.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = {}
        )]


class HighVoltage_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: High Voltage']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.ELECTRO

    def is_valid(self, match: Any) -> bool:
        """
        At least one charactor without maximum Energy.
        """
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if charactor.is_alive and charactor.charge < charactor.max_charge:
                return True
        return False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction]:
        """
        active charactor first to gain energy.
        """
        assert target is None
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if active_charactor.charge < active_charactor.max_charge:
            return [ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = active_charactor.position.charactor_idx,
                charge = 1,
            )]
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if (
                charactor.is_alive
                and charactor.charge < charactor.max_charge
            ):
                return [ChargeAction(
                    player_idx = self.position.player_idx,
                    charactor_idx = charactor.position.charactor_idx,
                    charge = 1,
                )]
        else:
            raise AssertionError('No charactor can be charged.')


class ImpetuousWinds_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Impetuous Winds']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.ANEMO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # all alive charactors except active charactor
        active_idx = match.player_tables[
            self.position.player_idx].active_charactor_idx
        return [
            charactor.position for (cid, charactor) in enumerate(
                match.player_tables[self.position.player_idx].charactors
            )
            if charactor.is_alive and cid != active_idx
        ]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateDiceAction | SwitchCharactorAction]:
        """
        Create one omni element dice
        """
        assert target is not None
        return [
            SwitchCharactorAction(
                player_idx = target.player_idx,
                charactor_idx = target.charactor_idx,
            ),
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = DieColor.OMNI,
                number = 1,
            ),
        ]


class EnduringRock_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Enduring Rock']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.GEO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create status
        """
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class SprawlingGreenery_3_3(ElementalResonanceCardBase):
    name: Literal['Elemental Resonance: Sprawling Greenery']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.DENDRO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | ChangeObjectUsageAction]:
        """
        Create status and add usage if exists. 
        """
        assert target is None
        ret: List[CreateObjectAction | ChangeObjectUsageAction] = [
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
        object_names = ['Burning Flame', 'Dendro Core', 'Catalyzing Field']
        status = match.player_tables[self.position.player_idx].team_status
        for s in status:
            if s.name in object_names:
                ret.append(ChangeObjectUsageAction(
                    object_position = s.position,
                    change_usage = 1,
                ))
        summons = match.player_tables[self.position.player_idx].summons
        for s in summons:
            if s.name in object_names:
                ret.append(ChangeObjectUsageAction(
                    object_position = s.position,
                    change_usage = 1,
                ))
        return ret


class NationResonanceCardBase(EventCardBase):
    faction: FactionType

    def get_deck_restriction(self) -> DeckRestriction:
        """
        For nation resonance cards, should contain at least 2 charactors of
        the corresponding faction.
        """
        return DeckRestriction(
            type = 'FACTION',
            name = self.faction.value,
            number = 2
        )


class WindAndFreedom_4_1(NationResonanceCardBase):
    name: Literal['Wind and Freedom']
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(same_dice_number = 1)
    faction: FactionType = FactionType.MONDSTADT

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create Wind and Freedom team status.
        """
        assert target is None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {
                'version': self.version
            },
        )]


class WindAndFreedom_3_7(WindAndFreedom_4_1):
    name: Literal['Wind and Freedom']
    version: Literal['3.7']


class StoneAndContracts_3_7(NationResonanceCardBase):
    name: Literal['Stone and Contracts']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(any_dice_number = 3)
    faction: FactionType = FactionType.LIYUE

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        create Stone and Contracts team status.
        """
        assert target is None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {},
        )]


class ThunderAndEternity_4_0(NationResonanceCardBase):
    name: Literal['Thunder and Eternity']
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost()
    faction: FactionType = FactionType.INAZUMA

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_dice_color(self, match: Any) -> DieColor:
        """
        Return omni color
        """
        return DieColor.OMNI

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[RemoveDiceAction | CreateDiceAction]:
        """
        remove all dice, and create same number dice
        """
        assert target is None
        player_table = match.player_tables[self.position.player_idx]
        dice_number = len(player_table.dice.colors)
        return [
            RemoveDiceAction(
                player_idx = self.position.player_idx,
                dice_idxs = list(range(dice_number)),
            ),
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = self.get_dice_color(match),
                number = len(player_table.dice.colors),
            )
        ]


class ThunderAndEternity_3_7(ThunderAndEternity_4_0):
    name: Literal['Thunder and Eternity']
    version: Literal['3.7']

    def get_dice_color(self, match: Any) -> str:
        """
        Convert all your Elemental Dice to the Type of the active character.
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return ELEMENT_TO_DIE_COLOR[charactor.element]


class NatureAndWisdom_3_7(NationResonanceCardBase):
    name: Literal['Nature and Wisdom']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)
    faction: FactionType = FactionType.SUMERU

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[DrawCardAction | GenerateSwitchCardRequestAction]:
        """
        draw 1 card, and switch any cards in your hand.
        """
        assert target is None
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 1,
                draw_if_filtered_not_enough = True
            ),
            GenerateSwitchCardRequestAction(
                player_idx = self.position.player_idx,
            )
        ]


class AbyssalSummons_3_3(NationResonanceCardBase):
    name: Literal['Abyssal Summons']
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 2)
    faction: FactionType = FactionType.MONSTER

    def is_valid(self, match: Any) -> bool:
        # if no place for summon, return False
        table = match.player_tables[self.position.player_idx]
        return len(table.summons) < match.config.max_summon_number

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create 1 Random Hilichurl Summon!
        """
        assert target is None
        assert not match.config.recreate_mode, (
            'Currently not support recreate mode.'
        )
        hilichurl_names = [
            'Cryo Hilichurl Shooter',
            'Electro Hilichurl Shooter',
            'Hilichurl Berserker',
            'Hydro Samachurl'
        ]
        # if already has above summons, do not re-create it
        summons = match.player_tables[self.position.player_idx].summons
        for summon in summons:
            if summon.name in hilichurl_names:
                hilichurl_names.remove(summon.name)
        assert len(hilichurl_names) > 0, 'No Hilichurl summon can be created.'
        selected_name = hilichurl_names[int(match._random() 
                                            * len(hilichurl_names))]
        return [CreateObjectAction(
            object_name = selected_name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.SUMMON,
                id = -1,
            ),
            object_arguments = {},
        )]


class FatuiConspiracy_3_7(NationResonanceCardBase):
    name: Literal['Fatui Conspiracy']
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    faction: FactionType = FactionType.FATUI

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create 1 Random Status
        """
        assert target is None
        assert not match.config.recreate_mode, (
            'Currently not support recreate mode.'
        )
        fatui_names = [
            'Fatui Ambusher: Cryo Cicin Mage',
            'Fatui Ambusher: Mirror Maiden',
            'Fatui Ambusher: Pyroslinger Bracer',
            'Fatui Ambusher: Electrohammer Vanguard'
        ]
        # if enemy already has above status, do not re-create it
        enemy_status = match.player_tables[
            1 - self.position.player_idx].team_status
        for status in enemy_status:
            if status.name in fatui_names:
                fatui_names.remove(status.name)
        assert len(fatui_names) > 0, 'No Fatui status can be created.'
        # create with random name
        selected_name = fatui_names[int(match._random() * len(fatui_names))]
        return [CreateObjectAction(
            object_name = selected_name,
            object_position = ObjectPosition(
                player_idx = 1 - self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {},
        )]


register_class(
    WovenCards_3_3 | ShatteringIce_3_3 | SoothingWater_3_3 | FerventFlames_3_3 
    | HighVoltage_3_3 | ImpetuousWinds_3_3 | EnduringRock_3_3 
    | SprawlingGreenery_3_3
)
register_class(
    WindAndFreedom_4_1 | StoneAndContracts_3_7 | ThunderAndEternity_4_0 
    | NatureAndWisdom_3_7 | AbyssalSummons_3_3 | FatuiConspiracy_3_7
    | WindAndFreedom_3_7 | ThunderAndEternity_3_7
)
