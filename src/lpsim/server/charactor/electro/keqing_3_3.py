from typing import Any, Dict, List, Literal

from ....utils.class_registry import register_class

from ...event import SkillEndEventArguments

from ...action import (
    Actions, CreateObjectAction, RemoveCardAction, SkillEndAction, 
    SwitchCharactorAction, UseSkillAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    AOESkillBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillBase, SkillTalent
)


# Skills


class StellarRestoration(ElementalSkillBase):
    name: Literal['Stellar Restoration'] = 'Stellar Restoration'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        If Lightning Stiletto in hand, do not create another one.
        """
        ret = super().get_actions(match)
        table = match.player_tables[self.position.player_idx]
        hands = table.hands[:]
        if table.using_hand is not None:
            hands.append(table.using_hand)
        found_stiletto = False
        for card in hands:
            if card.name == 'Lightning Stiletto':
                found_stiletto = True
                break
        if not found_stiletto and len(hands) < match.config.max_hand_size:
            # not found stiletto and hand not full
            position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.HAND,
                id = -1
            )
            ret.append(CreateObjectAction(
                object_name = 'Lightning Stiletto',
                object_position = position,
                object_arguments = {}
            ))
        return ret


class StarwardSword(ElementalBurstBase, AOESkillBase):
    name: Literal['Starward Sword'] = 'Starward Sword'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    back_damage: int = 3
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 3,
    )


# Talents


class ThunderingPenance_3_3(SkillTalent):
    name: Literal['Thundering Penance']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Keqing'] = 'Keqing'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )
    skill: Literal['Stellar Restoration'] = 'Stellar Restoration'


class LightningStiletto_3_3(SkillTalent):
    """
    From tests, Lightning Stiletto performs almost same of skill talent,
    except it will not equip the card to the charactor.
    (e.g. Vermillion Hereafter can decrease its cost, although it claimed that
    only can decrease the cost of talent or normal attack.)
    """
    name: Literal['Lightning Stiletto']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Keqing'] = 'Keqing'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Stellar Restoration'] = 'Stellar Restoration'
    newly_created: bool = True
    use_card: bool = False

    def get_charactor_position(self, match: Any) -> ObjectPosition | None:
        """
        Find alive charactor index. If not found, return -1
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            if (
                charactor.name == self.charactor_name 
                and charactor.is_alive
                and not charactor.is_stunned
            ):
                return charactor.position
        return None

    def is_valid(self, match: Any) -> bool:
        return self.get_charactor_position(match) is not None

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        pos = self.get_charactor_position(match)
        assert pos is not None
        return [pos]

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
        """
        find keqing position, switch to it and use elemental skill immediately.
        No need to remove this card, as it will be removed after skill done.
        """
        assert target is not None
        # update skill position
        skills: List[SkillBase] = match.get_object(target).skills
        for skill in skills:
            if skill.name == self.skill:
                break
        else:
            raise AssertionError('Skill not found')
        ret: List[Actions] = []
        # if not active, switch to it
        active_idx = match.player_tables[
            self.position.player_idx].active_charactor_idx
        if active_idx != target.charactor_idx:
            ret.append(SwitchCharactorAction(
                player_idx = self.position.player_idx,
                charactor_idx = target.charactor_idx,
            ))
        # use skill
        ret.append(UseSkillAction(
            skill_position = skill.position,
        ))
        # skill used, add SkillEndAction
        ret.append(SkillEndAction(
            position = skill.position,
            target_position = match.player_tables[
                1 - skill.position.player_idx
            ].get_active_charactor().position,
            skill_type = skill.skill_type,
        ))
        self.use_card = True
        return ret

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If our Keqing use elemental skill, remove this card and create electro
        infusion status for her.
        """
        ret: List[Actions] = []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            source_area = ObjectPositionType.HAND,
            target_area = ObjectPositionType.SKILL,
        ):
            # this card not in hand, or not our charactor use skill
            return []
        skill: SkillBase = match.get_object(event.action.position)
        if skill.name != self.skill:
            # not elemental skill
            return []
        if self.newly_created:
            # this card is newly created, mark False and do nothing.
            self.newly_created = False
            return []
        # remove this card
        table = match.player_tables[self.position.player_idx]
        hands = table.hands[:]
        if table.using_hand is not None:
            hands.append(table.using_hand)
        for i, card in enumerate(hands):
            if card.id == self.id:
                ret.append(RemoveCardAction(
                    position = self.position,
                    remove_type = 'USED' if self.use_card else 'BURNED'
                ))
                break
        else:
            raise AssertionError('Card not in hand')
        # generate args
        args: Dict = {
            'mark': 'Keqing'
        }
        charactor = match.player_tables[skill.position.player_idx].charactors[
            skill.position.charactor_idx]
        if charactor.talent is not None:
            args['usage'] = 3
            args['max_usage'] = 3
            args['talent_activated'] = True
        # create electro infusion status
        ret.append(CreateObjectAction(
            object_name = 'Electro Elemental Infusion',
            object_position = charactor.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_arguments = args,
        ))
        return ret


# charactor base


class Keqing_3_3(CharactorBase):
    name: Literal['Keqing']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | StellarRestoration | StarwardSword
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE,
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Yunlai Swordsmanship',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            StellarRestoration(),
            StarwardSword()
        ]


register_class(Keqing_3_3 | ThunderingPenance_3_3 | LightningStiletto_3_3)
