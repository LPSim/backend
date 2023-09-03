

from typing import Any, List, Literal

from ....action import CreateObjectAction

from ....event import SkillEndEventArguments

from .base import RoundEffectWeaponBase

from ....struct import Cost, ObjectPosition

from ....consts import CostLabels, ObjectPositionType, ObjectType, WeaponType


class TheBell(RoundEffectWeaponBase):
    name: Literal['The Bell']
    desc: str = (
        'The character deals +1 DMG. '
        'After the character uses a skill: Gives 1 Shield point to your '
        'active character. (Once per Round, stacks up to 2 points)'
    )
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    version: Literal['3.7'] = '3.7'
    cost_label: int = CostLabels.CARD.value | CostLabels.WEAPON.value
    weapon_type: WeaponType = WeaponType.CLAYMORE

    cost: Cost = Cost(same_dice_number = 3)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If self charactor use any skill, and have usage, create Rebellious
        Shield.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL
        ):
            # not self charactor use skill
            return []
        if self.usage == 0:
            # no usage
            return []
        self.usage -= 1
        return [CreateObjectAction(
            object_name = 'Rebellious Shield',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1
            ),
            object_arguments = {}
        )]


Claymores = TheBell | TheBell
