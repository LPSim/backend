from typing import Any, List, Literal

from ...event import RoundEndEventArguments

from ...summon.base import AttackerSummonBase

from ...modifiable_values import DamageIncreaseValue, DamageValue

from ...action import ActionTypes, Actions, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, PhysicalNormalAttackBase, 
    CharactorBase, SkillTalent
)


# Summons


class DandelionField(AttackerSummonBase):
    name: Literal['Dandelion Field'] = 'Dandelion Field'
    desc: str = (
        'End Phase: Deal 2 Anemo DMG, heal your active character for 1 HP.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    damage: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        If found Jean with talent, increase anemo damage by 1
        """
        if (
            value.damage_type != DamageType.DAMAGE
            or value.damage_elemental_type != DamageElementalType.ANEMO
            or value.position.player_idx != self.position.player_idx
            or value.target_position.player_idx == self.position.player_idx
        ):
            # not anemo damage, or not from our side attack enemy
            return value
        # find jean with talent
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if charactor.name == 'Jean' and charactor.talent is not None:
                # found, increase damage
                assert mode == 'REAL'
                value.damage += 1
                return value
        return value

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[
            self.position.player_idx].get_active_charactor()
        ret.append(MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = our_active.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost(),
                )
            ],
        ))
        return ret


# Skills


class GaleBlade(ElementalSkillBase):
    name: Literal['Gale Blade'] = 'Gale Blade'
    desc: str = (
        'Deals 3 Anemo DMG, the target is forcibly switched to the next '
        'character.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        next_idx = match.player_tables[
            1 - self.position.player_idx].next_charactor_idx()
        if next_idx is None:
            return ret
        # change charactor
        attack_action = ret[0]
        assert attack_action.type == ActionTypes.MAKE_DAMAGE
        attack_action.do_charactor_change = True
        attack_action.charactor_change_idx = next_idx
        return ret


class DandelionBreeze(ElementalBurstBase):
    name: Literal['Dandelion Breeze'] = 'Dandelion Breeze'
    desc: str = (
        'Heals all your characters for 2 HP, summons 1 Dandelion Field.'
    )
    damage: int = -2
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = [self.charge_self(-3)]
        charactors = match.player_tables[self.position.player_idx].charactors
        heal_action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [],
        )
        for charactor in charactors:
            if charactor.is_alive:
                heal_action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = self.damage,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = self.cost.copy(),
                    )
                )
        ret.append(heal_action)
        ret.append(self.create_summon('Dandelion Field'))
        return ret


# Talents


class LandsOfDandelion(SkillTalent):
    name: Literal['Lands of Dandelion']
    desc: str = (
        'Combat Action: When your active character is Jean, equip this card. '
        'After Jean equips this card, immediately use Dandelion Breeze once. '
        'When your Jean, who has this card equipped, is on the field, '
        'Dandelion Field will cause you to deal +1 Anemo DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Jean'] = 'Jean'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
        charge = 3
    )
    skill: DandelionBreeze = DandelionBreeze()


# charactor base


class Jean(CharactorBase):
    name: Literal['Jean']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Dandelion Knight" Jean'''
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | GaleBlade | DandelionBreeze
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: LandsOfDandelion | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GaleBlade(),
            DandelionBreeze(),
        ]
