from typing import Any, List, Literal

from ...event import GameStartEventArguments

from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Charactor status. DO NOT define here, define in server/status/characor_status
# Here is just example.


# Round status, will last for several rounds and disappear
# Skills


class SecretRiteChasmicSoulfarer(ElementalSkillBase):
    name: Literal[
        'Secret Rite: Chasmic Soulfarer'] = 'Secret Rite: Chasmic Soulfarer'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When talent equipped and level match, increase damage by 1
        """
        if self.is_talent_equipped(match):
            status = match.player_tables[self.position.player_idx].charactors[
                self.position.charactor_idx].status
            for s in status:
                if s.name == 'Pactsworn Pathclearer':  # pragma: no branch
                    if s.usage == 3 or s.usage == 5:
                        self.damage = 4
                    break
            else:
                raise AssertionError('No Pactsworn Pathclearer status')
        ret = super().get_actions(match)
        self.damage = 3
        return ret


class SacredRiteWolfsSwiftness(ElementalBurstBase):
    name: Literal[
        "Sacred Rite: Wolf's Swiftness"] = "Sacred Rite: Wolf's Swiftness"
    desc: str = (
        "Deals 4 Electro DMG. Pactsworn Pathclearer's Indwelling Level +2."
    )
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        attack and increase usage
        """
        ret = super().get_actions(match)
        status = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx].status
        for s in status:
            if s.name == 'Pactsworn Pathclearer':  # pragma: no branch
                ret.append(ChangeObjectUsageAction(
                    object_position = s.position,
                    change_type = 'DELTA',
                    change_usage = 2
                ))
                return ret
        else:
            raise AssertionError('No Pactsworn Pathclearer status')


class LawfulEnforcer(PassiveSkillBase):
    name: Literal['Lawful Enforcer'] = 'Lawful Enforcer'
    desc: str = (
        '(Passive) When the battle begins, this character gains Pactsworn '
        'Pathclearer.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain Pactsworn Pathclearer
        """
        return [self.create_charactor_status('Pactsworn Pathclearer')]


# Talents


class FeatherfallJudgment(SkillTalent):
    name: Literal['Featherfall Judgment']
    desc: str = (
        'Combat Action: When your active character is Cyno, equip this card. '
        'After Cyno equips this card, immediately use Secret Rite: Chasmic '
        'Soulfarer once. When your Cyno, who has this card equipped, uses '
        "Secret Rite: Chasmic Soulfarer with 3 or 5 levels of Pactsworn "
        "Pathclearer's Indwelling effect, deal +1 additional DMG."
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Cyno'] = 'Cyno'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: SecretRiteChasmicSoulfarer = SecretRiteChasmicSoulfarer()


# charactor base


class Cyno(CharactorBase):
    name: Literal['Cyno']
    version: Literal['3.3'] = '3.3'
    desc: str = (
        '''"Judicator of Secrets" Cyno'''
    )
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SecretRiteChasmicSoulfarer
        | SacredRiteWolfsSwiftness | LawfulEnforcer
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: FeatherfallJudgment | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = "Invoker's Spear",
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SecretRiteChasmicSoulfarer(),
            SacredRiteWolfsSwiftness(),
            LawfulEnforcer()
        ]
