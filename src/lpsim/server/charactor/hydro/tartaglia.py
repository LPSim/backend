from typing import Any, List, Literal


from ...modifiable_values import DamageValue
from ...event import (
    GameStartEventArguments, RoundEndEventArguments, SkillEndEventArguments
)
from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...struct import Cost

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, PassiveSkillBase, CharactorBase, SkillBase, 
    SkillTalent
)


# Skills


class AttachRiptideWhenSkillEnd(SkillBase):
    version: str

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When skill end, if is this skill, and target
        is alive, attach riptide to target.
        """
        if event.action.position.id != self.id:
            # not self skill
            return []
        target = match.player_tables[1 - self.position.player_idx].charactors[
            event.action.target_position.charactor_idx]
        if target.is_defeated:
            # target is defeated
            return []
        # attach riptide to target
        return [
            CreateObjectAction(
                object_name = 'Riptide',
                object_position = event.action.target_position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_arguments = { 'version': self.version }
            )
        ]


class FoulLegacyRagingTide(ElementalSkillBase, AttachRiptideWhenSkillEnd):
    name: Literal['Foul Legacy: Raging Tide'] = 'Foul Legacy: Raging Tide'
    desc: str = (
        'Switches to Melee Stance and deals 2 Hydro DMG, '
        'and attach Riptide to the target charactor.'
    )
    version: Literal['4.1'] = '4.1' 
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
            self.create_charactor_status(
                'Melee Stance',
                { 'version': self.version }
            ),
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.charge_self(1),
        ]


class HavocObliteration(ElementalBurstBase, AttachRiptideWhenSkillEnd):
    name: Literal['Havoc: Obliteration'] = 'Havoc: Obliteration'
    desc: str = (
        'Performs different attacks based on the current stance that '
        'Tartaglia is in. Ranged Stance - Flash of Havoc: Deal 5 Hydro DMG, '
        'reclaim 2 Energy, and apply Riptide to the target character. '
        'Melee Stance - Light of Obliteration: Deal 7 Hydro DMG.'
    )
    version: Literal['4.1'] = '4.1' 
    damage: int = 7
    ranged_damage: int = 5
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
            # ranged damage, and reclaim 2 energy. riptide will attach in
            # skill end.
            return [
                self.charge_self(-3),
                self.attack_opposite_active(
                    match, self.ranged_damage, DamageElementalType.HYDRO),
                self.charge_self(2),
            ]
        else:
            # 7 damage
            return super().get_actions(match)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If ranged stance, call super() to attach riptide.
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        ranged_found: bool = False
        for status in charactor.status:
            if status.name == 'Ranged Stance':
                ranged_found = True
                break
        if not ranged_found:
            # not ranged stance
            return []
        return super().event_handler_SKILL_END(event, match)


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
    version: Literal['4.1'] = '4.1'

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain ranged stance and system handler
        """
        return [
            self.create_charactor_status(
                'Ranged Stance',
                { 'version': self.version }
            ),
        ]


# Talents


class AbyssalMayhemHydrospout(SkillTalent):
    name: Literal['Abyssal Mayhem: Hydrospout']
    desc: str = (
        'Combat Action: When your active character is Tartaglia, equip this '
        'card. After Tartaglia equips this card, immediately use Foul Legacy: '
        'Raging Tide once. End Phase: Deals 1 Piercing DMG to the opponent '
        'active character if they have Riptide attached.'
    )
    version: Literal['4.1'] = '4.1'
    charactor_name: Literal['Tartaglia'] = 'Tartaglia'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )
    skill: FoulLegacyRagingTide = FoulLegacyRagingTide()
    only_active_charactor: bool = True

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Make 1 damage to character if affected by Riptide. When only active
        charactor (after 4.1), only check active charactor. Otherwise,
        check all charactors.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        ret: List[MakeDamageAction] = []
        active_idx = match.player_tables[
            1 - self.position.player_idx].active_charactor_idx
        for cidx, charactor in enumerate(
            match.player_tables[1 - self.position.player_idx].charactors
        ):
            if self.only_active_charactor and cidx != active_idx:
                continue
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
    version: Literal['4.1'] = '4.1'
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
