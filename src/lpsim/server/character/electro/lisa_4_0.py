from typing import Any, List, Literal, Tuple

from ....utils.class_registry import register_class

from ...summon.base import AttackerSummonBase

from ...event import (
    ChooseCharacterEventArguments,
    RoundPrepareEventArguments,
    SwitchCharacterEventArguments,
)

from ...action import Actions, CreateObjectAction, RemoveObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    CostLabels,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    PlayerActionLabels,
    WeaponType,
)
from ..character_base import (
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    TalentBase,
)


# Summons


class LightningRoseSummon_4_0(AttackerSummonBase):
    name: Literal["Lightning Rose"] = "Lightning Rose"
    version: Literal["4.0"] = "4.0"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 2


# Skills


class LightningTouch(ElementalNormalAttackBase):
    name: Literal["Lightning Touch"] = "Lightning Touch"
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = ElementalNormalAttackBase.get_cost(ElementType.ELECTRO)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Do attack; if charged attack, attach conductive
        """
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack
            return super().get_actions(match)
        return super().get_actions(match) + [
            self.create_opposite_character_status(match, "Conductive", {})
        ]


class VioletArc(ElementalSkillBase):
    name: Literal["Violet Arc"] = "Violet Arc"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If Conductive not attached, attach Conductive
        otherwise, increase damage.
        """
        target = match.player_tables[
            1 - self.position.player_idx
        ].get_active_character()
        status = target.status
        conductive = None
        for s in status:
            if s.name == "Conductive":
                conductive = s
                break
        if conductive is None:
            # no conductive
            return super().get_actions(match) + [
                self.create_opposite_character_status(match, "Conductive", {})
            ]
        else:
            # has conductive
            self.damage += conductive.usage
            ret = super().get_actions(match)
            self.damage = 2
            ret = [RemoveObjectAction(object_position=conductive.position)] + ret
            return ret


class LightningRose(ElementalBurstBase):
    name: Literal["Lightning Rose"] = "Lightning Rose"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [self.create_summon(self.name)]


# Talents


class PulsatingWitch_4_0(TalentBase):
    name: Literal["Pulsating Witch"]
    version: Literal["4.0"] = "4.0"
    character_name: Literal["Lisa"] = "Lisa"
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=1)
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value | CostLabels.EQUIPMENT.value
    )
    usage: int = 1

    def is_valid(self, match: Any) -> bool:
        """
        Only corresponding character is active character can equip this card.
        """
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError("Talent is not in hand")
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        All ayaka are targets
        """
        assert self.position.area != ObjectPositionType.CHARACTER
        ret: List[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].characters:
            if c.name == self.character_name and c.is_alive:
                ret.append(c.position)
        return ret

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        return (PlayerActionLabels.CARD.value | PlayerActionLabels.SKILL.value, False)

    def _attach_conductive_to_opposite_active(
        self,
        event: SwitchCharacterEventArguments | ChooseCharacterEventArguments,
        match: Any,
    ) -> List[CreateObjectAction]:
        if (
            event.action.player_idx != self.position.player_idx
            or event.action.character_idx != self.position.character_idx
        ):
            # not to this character
            return []
        target = match.player_tables[
            1 - self.position.player_idx
        ].get_active_character()
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        return [
            CreateObjectAction(
                object_name="Conductive",
                object_position=target.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            )
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset usage
        """
        self.usage = 1
        return []

    def event_handler_SWITCH_CHARACTER(
        self, event: SwitchCharacterEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        return self._attach_conductive_to_opposite_active(event, match)

    def event_handler_CHOOSE_CHARACTER(
        self, event: ChooseCharacterEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        return self._attach_conductive_to_opposite_active(event, match)


# character base


class Lisa_4_0(CharacterBase):
    name: Literal["Lisa"]
    version: Literal["4.0"] = "4.0"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[LightningTouch | VioletArc | LightningRose] = []
    faction: List[FactionType] = [FactionType.MONDSTADT]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [LightningTouch(), VioletArc(), LightningRose()]


register_class(Lisa_4_0 | PulsatingWitch_4_0 | LightningRoseSummon_4_0)
