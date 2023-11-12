from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...consts import DieColor

from ...struct import Cost
from ...action import Actions
from ..charactor_base import ElementalNormalAttackBase, SkillTalent
from .sangonomiya_kokomi_3_6 import SangonomiyaKokomi_3_6 as SK_3_6
from .sangonomiya_kokomi_3_6 import NereidsAscension as NA_3_6
from .sangonomiya_kokomi_3_6 import KuragesOath


class NereidsAscension(NA_3_6):
    desc: str = (
        'Deals 3 Hydro DMG. This character gains Ceremonial Garment.'
    )
    damage: int = 3

    def get_actions(self, match: Any) -> List[Actions]:
        """
        No healing
        """
        return super(NA_3_6, self).get_actions(match) + [
            self.create_charactor_status('Ceremonial Garment'),
        ]


class TamakushiCasket_3_5(SkillTalent):
    name: Literal['Tamakushi Casket']
    desc: str = (
        'Combat Action: When your active character is Sangonomiya Kokomi, '
        'equip this card. After Sangonomiya Kokomi equips this card, '
        "immediately use Nereid's Ascension once. When your Sangonomiya "
        "Kokomi, who has this card equipped, uses Nereid's Ascension: If "
        "Bake-Kurage is on the field, its Usage(s) will be refreshed. While "
        'Ceremonial Garment exists, Bake-Kurage deals +1 DMG'
    )
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Sangonomiya Kokomi'] = 'Sangonomiya Kokomi'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )
    skill: Literal["Nereid's Ascension"] = "Nereid's Ascension"


class SangonomiyaKokomi_3_5(SK_3_6):
    version: Literal['3.5']
    skills: List[
        ElementalNormalAttackBase | KuragesOath | NereidsAscension
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'The Shape of Water',
                damage_type = self.element,
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            KuragesOath(),
            NereidsAscension(),
        ]


register_class(SangonomiyaKokomi_3_5 | TamakushiCasket_3_5)
