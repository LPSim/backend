from typing import List

from utils import BaseModel


class SkillActionArguments(BaseModel):
    """
    Arguments used in getting skill actions.
    """
    player_id: int
    our_active_charactor_id: int
    enemy_active_charactor_id: int
    our_charactors: List[int]
    enemy_charactors: List[int]
