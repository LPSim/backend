from typing import Any, List, Literal

from ...modifiable_values import DamageIncreaseValue

from ...event import GameStartEventArguments

from ...summon.base import AttackerSummonBase

from ...action import Actions, ChargeAction, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, PhysicalNormalAttackBase, 
    PassiveSkillBase, CharactorBase, SkillBase, SkillTalent
)


# Summons


class EyeOfStormyJudgment(AttackerSummonBase):
    name: Literal['Eye of Stormy Judgment'] = 'Eye of Stormy Judgment'
    desc: str = (
        'End Phase: Deal 1 Electro DMG. '
        "When this Summon is on the field: Your characters' Elemental Bursts "
        'deal +1 DMG.'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        assert mode == 'REAL'
        if value.position.player_idx != self.position.player_idx:
            # not self, not modify
            return value
        if value.position.area != ObjectPositionType.SKILL:
            # not skill, not modify
            return value
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        skill: SkillBase = match.get_object(value.position)
        if skill.skill_type != SkillType.ELEMENTAL_BURST:
            # not burst, not modify
            return value
        # add damage
        value.damage += 1
        return value


# Skills


class TranscendenceBalefulOmen(ElementalSkillBase):
    name: Literal[
        'Transcendence: Baleful Omen'] = 'Transcendence: Baleful Omen'
    desc: str = '''Summons 1 Eye of Stormy Judgment'''
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object
        """
        return [
            self.charge_self(1),
            self.create_summon('Eye of Stormy Judgment')
        ]


class SecretArtMusouShinsetsu(ElementalBurstBase):
    name: Literal[
        'Secret Art: Musou Shinsetsu'] = 'Secret Art: Musou Shinsetsu'
    desc: str = (
        'Deals 3 Electro DMG. All of your other characters gain 2 Energy.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        table = match.player_tables[self.position.player_idx]
        for cid, charactor in enumerate(table.charactors):
            if charactor.is_alive and cid != self.position.charactor_idx:
                ret.append(ChargeAction(
                    player_idx = self.position.player_idx,
                    charactor_idx = cid,
                    charge = 2,
                ))
        return ret


class ChakraDesiderata(PassiveSkillBase):
    name: Literal['Chakra Desiderata'] = 'Chakra Desiderata'
    desc: str = (
        '(Passive) When the battle begins, this character gains '
        'Chakra Desiderata.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain stealth
        """
        return [self.create_charactor_status(self.name)]


# Talents


class WishesUnnumbered(SkillTalent):
    name: Literal['Wishes Unnumbered']
    desc: str = (
        'Combat Action: When your active character is Raiden Shogun, '
        'equip this card. After Raiden Shogun equips this card, immediately '
        'use Secret Art: Musou Shinsetsu once. When your Raiden Shogun, who '
        'has this card equipped, uses Secret Art: Musou Shinsetsu, it will '
        'deal +1 additional DMG for every point of Resolve consumed.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Raiden Shogun'] = 'Raiden Shogun'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: SecretArtMusouShinsetsu = SecretArtMusouShinsetsu()


# charactor base


class RaidenShogun(CharactorBase):
    name: Literal['Raiden Shogun']
    version: Literal['3.7'] = '3.7'
    desc: str = '''"Plane of Euthymia" Raiden Shogun'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | TranscendenceBalefulOmen 
        | SecretArtMusouShinsetsu | ChakraDesiderata
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: WishesUnnumbered | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Origin',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TranscendenceBalefulOmen(),
            SecretArtMusouShinsetsu(),
            ChakraDesiderata(),
        ]
