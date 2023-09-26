from typing import Any, List, Literal
from ...modifiable_values import DamageValue

from ...summon.base import AttackerSummonBase

from ...event import ReceiveDamageEventArguments, SkillEndEventArguments

from ...action import (
    Actions, ChangeObjectUsageAction, MakeDamageAction
)
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DamageType, DieColor, ElementType, 
    ElementalReactionType, FactionType, ObjectPositionType, SkillType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Summons


class CryoCicins(AttackerSummonBase):
    name: Literal['Cryo Cicins'] = 'Cryo Cicins'
    desc: str = (
        'End Phase: Deal 1 Cryo DMG. (Can stack. Max 3 stacks.) '
        'After Fatui Cryo Cicin Mage performs a Normal Attack: This card '
        'gains 1 Usage(s). After your Fatui Cryo Cicin Mage takes Elemental '
        'Reaction DMG: This card loses 1 Usage(s).'
    )
    version: Literal['4.1'] = '4.1'
    usage: int = 2
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1
    renew_type: Literal['ADD'] = 'ADD'
    decrease_only_self_damage: bool = True

    over_maximum: bool = False

    def renew(self, new_status: 'CryoCicins') -> None:
        if self.usage + new_status.usage > self.max_usage:
            self.over_maximum = True
        return super().renew(new_status)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction | MakeDamageAction]:
        if event.action.position.player_idx != self.position.player_idx:
            # not our player skill made damage, do nothing
            self.over_maximum = False
            return []
        assert event.action.position.area == ObjectPositionType.SKILL
        charactors = match.player_tables[self.position.player_idx].charactors
        charactor = charactors[event.action.position.charactor_idx]
        if charactor.name != 'Fatui Cryo Cicin Mage':
            # not Fatui Cryo Cicin Mage, do nothing
            self.over_maximum = False
            return []
        ret: List[ChangeObjectUsageAction | MakeDamageAction] = []
        if event.action.skill_type == SkillType.NORMAL_ATTACK:
            # change usage
            ret += [ChangeObjectUsageAction(
                object_position = self.position,
                change_type = 'DELTA',
                change_usage = 1,
                max_usage = self.max_usage
            )]
            if self.usage + 1 > self.max_usage:
                self.over_maximum = True
        # if over_maximum and charactor has talent, 2 damage to opposite active
        if self.over_maximum and charactor.talent is not None:
            target_charactor = match.player_tables[
                1 - self.position.player_idx].get_active_charactor()
            ret.append(MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = 1 - self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target_charactor.position,
                        damage = 2,
                        damage_elemental_type = self.damage_elemental_type,
                        cost = Cost(),
                    )
                ]
            ))
        self.over_maximum = False
        return ret

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        if (
            event.final_damage.target_position.player_idx 
            != self.position.player_idx
            or event.elemental_reaction == ElementalReactionType.NONE
            or event.final_damage.damage_type != DamageType.DAMAGE
        ):
            # not self player receive damage, or no elemental reaction,
            # or not damage
            return []
        target = match.player_tables[
            event.final_damage.target_position.player_idx
        ].charactors[
            event.final_damage.target_position.charactor_idx
        ]
        if (
            self.decrease_only_self_damage
            and target.name != 'Fatui Cryo Cicin Mage'
        ):
            # only decrease in self damage
            return []
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = -1
        )]


# Skills


def find_cryo_cicins(
    position: ObjectPosition, match: Any, usage: int
) -> Any | None:
    """
    Find cicins based on self position and match. then if with usage will 
    exceed max usage, return cicin position. otherwise, return None.
    """
    summons = match.player_tables[position.player_idx].summons
    for summon in summons:
        if (
            summon.name == 'Cryo Cicins' 
            and summon.usage + usage > summon.max_usage
        ):
            return summon
    return None


class CicinIcicle(ElementalNormalAttackBase):
    name: Literal['Cicin Icicle'] = 'Cicin Icicle'
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = ElementalNormalAttackBase.get_cost(ElementType.CRYO)


class MistySummons(ElementalSkillBase):
    name: Literal['Misty Summons'] = 'Misty Summons'
    desc: str = '''Deals 1 Cryo DMG, summons Cryo Cicins.'''
    version: Literal['4.1'] = '4.1'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon('Cryo Cicins', { 'version': self.version }),
        ]


class BlizzardBranchBlossom(ElementalBurstBase):
    name: Literal['Blizzard, Branch, Blossom'] = 'Blizzard, Branch, Blossom'
    desc: str = (
        'Deals 5 Cryo DMG, grants this character Cryo Application, '
        'creates 1 Flowing Cicin Shield.'
    )
    damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        # max usage, so find regardless of its current usage
        cicin = find_cryo_cicins(self.position, match, 999)
        args = {}
        if cicin is not None:
            args['usage'] = 1 + cicin.usage
            args['max_usage'] = 1 + cicin.usage
        return super().get_actions(match) + [
            self.element_application_self(match, DamageElementalType.CRYO),
            self.create_team_status('Flowing Cicin Shield', args)
        ]


# Talents


class CicinsColdGlare(SkillTalent):
    name: Literal["Cicin's Cold Glare"]
    desc: str = (
        'Combat Action: When your active character is Fatui Cryo Cicin Mage, '
        'equip this card. After Fatui Cryo Cicin Mage equips this card, '
        'immediately use Misty Summons once. After your Fatui Cryo Cicin '
        "Mage, who has this card equipped, uses a Skill: If Cryo Cicins' "
        'Usage(s) have exceeded their upper limit, deal 2 Cryo DMG.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Fatui Cryo Cicin Mage'] = 'Fatui Cryo Cicin Mage'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )
    skill: MistySummons = MistySummons()


# charactor base


class FatuiCryoCicinMage(CharactorBase):
    name: Literal['Fatui Cryo Cicin Mage']
    version: Literal['4.1'] = '4.1'
    desc: str = '''"Cicin of the Hollow Mist" Cryo Cicin Mage'''
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        CicinIcicle | MistySummons | BlizzardBranchBlossom
    ] = []
    faction: List[FactionType] = [
        FactionType.FATUI
    ]
    weapon_type: WeaponType = WeaponType.OTHER
    talent: CicinsColdGlare | None = None

    def _init_skills(self) -> None:
        self.skills = [
            CicinIcicle(),
            MistySummons(),
            BlizzardBranchBlossom()
        ]
