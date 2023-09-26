from typing import Any, List, Literal

from ....consts import ObjectPositionType, SkillType, WeaponType

from ....action import ChargeAction
from ....event import SkillEndEventArguments
from ....struct import Cost
from .base import RoundEffectWeaponBase


class FavoniusBase(RoundEffectWeaponBase):
    name: str
    desc: str = (
        'The character deals +1 DMG. '
        'After the character uses an Elemental Skill: The character gains one '
        'additional Energy. (Once per Round)'
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: str
    weapon_type: WeaponType
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        if self charactor use elemental skill, charge one more
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self charactor or not equipped
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        return [ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = self.position.charactor_idx,
            charge = 1
        )]


class FavoniusSword(FavoniusBase):
    name: Literal['Favonius Sword']
    version: Literal['3.7'] = '3.7'
    weapon_type: Literal[WeaponType.SWORD] = WeaponType.SWORD


FavoniusWeapons = FavoniusSword | FavoniusSword
