from typing import Any, List, Literal

from ...event import GameStartEventArguments

from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, PhysicalNormalAttackBase, 
    PassiveSkillBase, CharactorBase, SkillTalent
)


# Skills


class VolatileSporeCloud(ElementalSkillBase):
    name: Literal['Volatile Spore Cloud'] = 'Volatile Spore Cloud'
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )


class FeatherSpreading(ElementalBurstBase):
    name: Literal['Feather Spreading'] = 'Feather Spreading'
    desc: str = (
        'Deals 4 Dendro DMG, then consumes all Radical Vitality stacks. '
        'For each stack consumed, this instance deals +1 DMG.'
    )
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Base on usage, increase damage and reset usage
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        found_status: Any = None
        for status in charactor.status:
            if status.name == 'Radical Vitality':  # pragma: no branch
                found_status = status
                break
        else:
            raise AssertionError('Radical Vitality not found')
        if found_status.usage == 0:
            # no usage, do nothing
            return super().get_actions(match)
        # increase damage
        self.damage += found_status.usage
        ret = super().get_actions(match)
        self.damage = 4
        ret.append(ChangeObjectUsageAction(
            object_position = found_status.position,
            change_type = 'DELTA',
            change_usage = - found_status.usage
        ))
        return ret


class RadicalVitality(PassiveSkillBase):
    name: Literal['Radical Vitality'] = 'Radical Vitality'
    desc: str = (
        '(Passive) When the battle begins, this character gains Radical '
        'Vitality.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain stealth
        """
        return [self.create_charactor_status(self.name)]


# Talents


class ProliferatingSpores(SkillTalent):
    name: Literal['Proliferating Spores']
    desc: str = (
        'Combat Action: When your active character is Jadeplume Terrorshroom, '
        'equip this card. After Jadeplume Terrorshroom equips this card, '
        'immediately use Volatile Spore Cloud once. Your Jadeplume '
        'Terrorshroom, who has this card equipped, can accumulate 1 more '
        'stack of Radical Vitality.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal[
        'Jadeplume Terrorshroom'] = 'Jadeplume Terrorshroom'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )
    skill: VolatileSporeCloud = VolatileSporeCloud()

    def equip(self, match: Any) -> List[CreateObjectAction]:
        """
        When equip, re-create Radical Vitality with 1 more max usage
        """
        return [self.skill.create_charactor_status(
            'Radical Vitality', 
            { 'max_usage': 4 }
        )]


# charactor base


class JadeplumeTerrorshroom(CharactorBase):
    name: Literal['Jadeplume Terrorshroom']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Lord of Fungi" Jadeplume Terrorshroom'''
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | VolatileSporeCloud | FeatherSpreading 
        | RadicalVitality
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER
    talent: ProliferatingSpores | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Majestic Dance',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            VolatileSporeCloud(),
            FeatherSpreading(),
            RadicalVitality()
        ]
