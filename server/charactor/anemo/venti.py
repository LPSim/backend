from typing import Any, List, Literal

from server.summon.base import SummonBase

from ...summon.base import AttackerSummonBase

from ...event import ReceiveDamageEventArguments, RoundEndEventArguments

from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    ElementalReactionType, FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class Stormeye(AttackerSummonBase):
    name: Literal['Stormeye'] = 'Stormeye'
    desc: str = (
        'End Phase: Deal 2 Anemo DMG. Your opponent switches to: Character '
        'Closest to Your Current Active Character. '
        'After your character or Summon triggers a Swirl reaction: Convert '
        'the Elemental Type of this card and change its DMG dealt to the '
        'element Swirled. (Can only be converted once before leaving the '
        'field)'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    damage: int = 2

    def renew(self, new_status: SummonBase) -> None:
        """
        When renew, also renew damage elemental type.
        """
        super().renew(new_status)
        self.damage_elemental_type = DamageElementalType.ANEMO

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        When anyone receives damage, and has swirl reaction, and made by
        our charactor or summon, and current damage type is anemo, 
        change stormeye damage element.

        TODO: how to consider made by status? currently all damage made from
        our player are considered valid.
        """
        if self.damage_elemental_type != DamageElementalType.ANEMO:
            # already changed, do nothing
            return []
        if event.final_damage.position.player_idx != self.position.player_idx:
            # not our player made damage, do nothing
            return []
        if event.final_damage.element_reaction != ElementalReactionType.SWIRL:
            # not swirl reaction, do nothing
            return []
        elements = event.final_damage.reacted_elements
        assert elements[0] == ElementType.ANEMO, 'First element must be anemo'
        # do type change
        self.damage_elemental_type = ELEMENT_TO_DAMAGE_TYPE[elements[1]]
        return []

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Need to change enemy active
        """
        ret = super().event_handler_ROUND_END(event, match)
        our_active = match.player_tables[
            self.position.player_idx].active_charactor_idx
        target_charactors = match.player_tables[
            1 - self.position.player_idx].charactors
        target_idx = our_active
        if target_charactors[target_idx].is_defeated:
            # need to choose another charactor
            for idx, charactor in enumerate(target_charactors):
                if not charactor.is_defeated:
                    target_idx = idx
                    break
            else:
                raise AssertionError('No charactor alive')
        assert len(ret) == 1
        ret[0].do_charactor_change = True
        ret[0].charactor_change_idx = target_idx
        return ret


# Skills


class SkywardSonnet(ElementalSkillBase):
    name: Literal['Skyward Sonnet'] = 'Skyward Sonnet'
    desc: str = '''Deals 2 Anemo DMG, creates 1 Stormzone.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        position = ObjectPosition(
            player_idx = self.position.player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1
        )
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        assert charactor.name == 'Venti'
        talent_activated = False
        if charactor.talent is not None:
            talent_activated = True
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name = 'Stormzone',
                object_position = position,
                object_arguments = {
                    'talent_activated': talent_activated
                }
            )
        ]


class WindsGrandOde(ElementalBurstBase):
    name: Literal["Wind's Grand Ode"] = "Wind's Grand Ode"
    desc: str = '''Deals 2 Anemo DMG, summons 1 Stormeye.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        position = ObjectPosition(
            player_idx = self.position.player_idx,
            area = ObjectPositionType.SUMMON,
            id = -1
        )
        # create summon first, so it can change element immediately.
        return [
            CreateObjectAction(
                object_name = 'Stormeye',
                object_position = position,
                object_arguments = {}
            )
        ] + super().get_actions(match)


# Talents


class EmbraceOfWinds(SkillTalent):
    name: Literal['Embrace of Winds']
    desc: str = (
        'Combat Action: When your active character is Venti, equip this card. '
        'After Venti equips this card, immediately use Skyward Sonnet once. '
        'After a Stormzone created by your Venti, who has this card equipped, '
        'is triggered, the next Normal Attack performed by your character in '
        'this Round will cost 1 less Unaligned Element.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Venti'] = 'Venti'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )
    skill: SkywardSonnet = SkywardSonnet()


# charactor base


class Venti(CharactorBase):
    name: Literal['Venti']
    version: Literal['3.7'] = '3.7'
    desc: str = '''"Windborne Bard" Venti'''
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | SkywardSonnet | WindsGrandOde
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.BOW
    talent: EmbraceOfWinds | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Divine Marksmanship',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SkywardSonnet(),
            WindsGrandOde()
        ]


# finally, modify server/charactor/(element)/__init__.py
