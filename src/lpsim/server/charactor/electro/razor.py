from typing import Any, List, Literal

from ...event import SkillEndEventArguments

from ...action import Actions, ChargeAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, SkillType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class ClawAndThunder(ElementalSkillBase):
    name: Literal['Claw and Thunder'] = 'Claw and Thunder'
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = ElementalSkillBase.get_cost(ElementType.ELECTRO)


class LightningFang(ElementalBurstBase):
    name: Literal['Lightning Fang'] = 'Lightning Fang'
    desc: str = (
        'Deals 3 Electro DMG. This character gains The Wolf Within.'
    )
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_charactor_status('The Wolf Within')
        ]


# Talents


class Awakening(SkillTalent):
    name: Literal['Awakening']
    desc: str = (
        'Combat Action: When your active character is Razor, equip this card. '
        'After Razor equips this card, immediately use Claw and Thunder once. '
        'After your Razor, who has this card equipped, uses Claw and Thunder: '
        '1 of your Electro characters gains 1 Energy. '
        '(Active Character prioritized)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Razor'] = 'Razor'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4
    )
    skill: ClawAndThunder = ClawAndThunder()

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        If equipped and use elemental skill, charge one of our electro 
        charactor
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not equipped, or this charactor use skill
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        # find charge target
        table = match.player_tables[self.position.player_idx]
        charactors = table.charactors
        active = charactors[table.active_charactor_idx]
        target_idx = -1
        if (
            active.element == ElementType.ELECTRO
            and active.charge < active.max_charge
        ):
            # active electro and not full charge
            target_idx = table.active_charactor_idx
        else:
            # check other charactors
            for chraractor_idx, charactor in enumerate(charactors):
                if (
                    charactor.element == ElementType.ELECTRO
                    and charactor.charge < charactor.max_charge
                    and charactor.is_alive
                ):
                    target_idx = chraractor_idx
                    break
        if target_idx == -1:
            # no target
            return []
        # charge target
        return [ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = target_idx,
            charge = 1
        )]

# charactor base


class Razor(CharactorBase):
    name: Literal['Razor']
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Wolf Boy" Razor'''
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ClawAndThunder | LightningFang
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE
    talent: Awakening | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Steel Fang',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ClawAndThunder(),
            LightningFang()
        ]
