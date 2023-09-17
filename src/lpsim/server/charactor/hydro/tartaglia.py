from typing import Any, List, Literal


from ...modifiable_values import DamageValue
from ...event import GameStartEventArguments, RoundEndEventArguments
from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillTalent
)


# Skills


class FoulLegacyRagingTide(ElementalSkillBase):
    name: Literal['Foul Legacy: Raging Tide'] = 'Foul Legacy: Raging Tide'
    desc: str = '''Switches to Melee Stance and deals 2 Hydro DMG.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        create object then attack
        """
        return [
            self.create_charactor_status('Melee Stance'),
            self.charge_self(1),
            self.attack_opposite_active(match, self.damage, self.damage_type)
        ]


class HavocObliteration(ElementalBurstBase):
    name: Literal['Havoc: Obliteration'] = 'Havoc: Obliteration'
    desc: str = (
        'Performs different attacks based on the current stance that '
        'Tartaglia is in. Ranged Stance - Flash of Havoc: Deal 4 Hydro DMG, '
        'reclaim 2 Energy, and apply Riptide to the target character. '
        'Melee Stance - Light of Obliteration: Deal 7 Hydro DMG.'
    )
    damage: int = 7
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        ranged_found: bool = False
        melee_found: bool = False
        for status in charactor.status:
            if status.name == 'Ranged Stance':
                ranged_found = True
            elif status.name == 'Melee Stance':  # pragma: no branch
                melee_found = True
        if ranged_found and melee_found:
            raise AssertionError('Cannot be both ranged and melee stance')
        if not (ranged_found or melee_found):
            raise AssertionError('Must be ranged or melee stance')
        if ranged_found:
            # 4 damage, and reclaim 2 energy
            return [
                self.charge_self(-3),
                self.attack_opposite_active(match, 4, 
                                            DamageElementalType.HYDRO),
                self.charge_self(2),
            ]
        else:
            # 7 damage
            return super().get_actions(match)


class TideWithholder(PassiveSkillBase):
    """
    Only generate Ranged Stance at game start, and generate riptide event
    handler for system. status swicth will be controlled by two status 
    themself.
    """
    name: Literal['Tide Withholder'] = 'Tide Withholder'
    desc: str = (
        '(Passive) When the battle begins, this character gains Ranged '
        'Stance. Once the Melee Stance attached to the character ends, '
        'reapplies Ranged Stance.'
    )

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain ranged stance and system handler
        """
        return [
            self.create_charactor_status('Ranged Stance'),
            CreateObjectAction(
                object_name = 'Riptide',
                object_position = ObjectPosition(
                    player_idx = -1,
                    area = ObjectPositionType.SYSTEM,
                    id = 0
                ),
                object_arguments = {}
            )
        ]


# Talents


class AbyssalMayhemHydrospout(SkillTalent):
    name: Literal['Abyssal Mayhem: Hydrospout']
    desc: str = (
        'Combat Action: When your active character is Tartaglia, equip this '
        'card. After Tartaglia equips this card, immediately use Foul Legacy: '
        'Raging Tide once. End Phase: Deals 1 Piercing DMG to all opposing '
        'characters affected by Riptide.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Tartaglia'] = 'Tartaglia'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
    )
    skill: FoulLegacyRagingTide = FoulLegacyRagingTide()

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Make 1 damage to all opposing characters affected by Riptide.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        ret: List[MakeDamageAction] = []
        for charactor in (
            match.player_tables[1 - self.position.player_idx].charactors
        ):
            for status in charactor.status:
                if status.name == 'Riptide':
                    ret.append(MakeDamageAction(
                        source_player_idx = self.position.player_idx,
                        target_player_idx = 1 - self.position.player_idx,
                        damage_value_list = [
                            DamageValue(
                                position = self.position,
                                damage_type = DamageType.DAMAGE,
                                target_position = charactor.position,
                                damage = 1,
                                damage_elemental_type 
                                = DamageElementalType.PIERCING,
                                cost = Cost(),
                            )
                        ]
                    ))
                    break
        return ret


# charactor base


class Tartaglia(CharactorBase):
    name: Literal['Tartaglia']
    version: Literal['3.7'] = '3.7'
    desc: str = '"Childe" Tartaglia'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | FoulLegacyRagingTide
        | HavocObliteration | TideWithholder
    ] = []
    faction: List[FactionType] = [
        FactionType.FATUI
    ]
    weapon_type: WeaponType = WeaponType.BOW
    talent: AbyssalMayhemHydrospout | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Cutting Torrent',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            FoulLegacyRagingTide(),
            HavocObliteration(),
            TideWithholder(),
        ]
