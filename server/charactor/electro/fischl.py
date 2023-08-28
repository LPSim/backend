from typing import List, Literal, Any

from ...event import SkillEndEventArguments

from ...action import Actions, CreateObjectAction, MakeDamageAction
from ...consts import (
    ElementType, FactionType, SkillType, WeaponType, DamageElementalType,
    ObjectPositionType, DamageType, DieColor
)
from ..charactor_base import (
    PhysicalNormalAttackBase, ElementalSkillBase, ElementalBurstBase, 
    CharactorBase, SkillTalent
)
from ...struct import DamageValue, Cost
from ...summon.base import AttackerSummonBase


class Nightrider(ElementalSkillBase):
    name: Literal['Nightrider'] = 'Nightrider'
    desc: str = 'Deals 1 Electro DMG, summons 1 Oz.'
    element: ElementType = ElementType.ELECTRO
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        position = self.position.copy(deep = True)
        position.area = ObjectPositionType.SUMMON
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name = 'Oz',
                object_position = position,
                object_arguments = {}
            )
        ]


class MidnightPhantasmagoria(ElementalBurstBase):
    name: Literal['Midnight Phantasmagoria'] = 'Midnight Phantasmagoria'
    desc: str = (
        'Deals 4 Electro DMG, deals 2 Piercing DMG to all opposing characters '
        'on standby.'
    )
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        assert len(ret) > 0
        assert ret[-1].type == 'MAKE_DAMAGE'
        ret[-1].damage_value_list.append(
            DamageValue(
                position = self.position.copy(deep = True),
                id = self.id,
                damage_type = DamageType.DAMAGE,
                damage = 2,
                damage_elemental_type = DamageElementalType.PIERCING,
                charge_cost = self.cost.charge,
                target_player = 'ENEMY',
                target_charactor = 'BACK',
            )
        )
        return ret


class StellarPredator(SkillTalent):
    name: Literal['Stellar Predator']
    charactor_name: str = 'Fischl'
    version: Literal['3.3'] = '3.3'
    desc: str = (
        'Combat Action: When your active character is Fischl, equip this '
        'card. After Fischl equips this card, immediately use Nightrider '
        'once. When your Fischl, who has this card equipped, creates an Oz, '
        'and after Fischl uses a Normal Attack: Deal 2 Electro DMG. '
        '(Consumes Usage(s))'
    )
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Nightrider = Nightrider()


class Oz(AttackerSummonBase):
    name: Literal['Oz']
    desc: str = '''End Phase: Deal 1 Electro DMG.'''
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1
    renew_type: Literal['RESET_WITH_MAX'] = 'RESET_WITH_MAX'

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments
    ) -> list[MakeDamageAction]:
        """
        If Fischl made normal attack and with talent, make 2 electro damage 
        to front.
        """
        match = event.match
        action = event.action
        if action.skill_type != SkillType.NORMAL_ATTACK:
            # not using normal attack
            return []
        if self.position.player_id != action.player_id:
            # not attack by self
            return []
        charactor = match.player_tables[action.player_id].charactors[
            action.charactor_id
        ]
        if (
            charactor.talent is not None and charactor.name == 'Fischl'
            and charactor.talent.name == 'Stellar Predator'
        ):
            # match, decrease usage, attack.
            # after make damage, will trigger usage check, so no need to
            # add RemoveObjectAction here.
            assert self.usage > 0
            self.usage -= 1
            return [
                MakeDamageAction(
                    player_id = self.position.player_id,
                    target_id = 1 - self.position.player_id,
                    damage_value_list = [
                        DamageValue(
                            position = self.position,
                            id = self.id,
                            damage_type = DamageType.DAMAGE,
                            damage = 2,
                            damage_elemental_type = self.damage_elemental_type,
                            charge_cost = 0,
                            target_player = 'ENEMY',
                            target_charactor = 'ACTIVE'
                        )
                    ],
                    charactor_change_rule = 'NONE',
                )
            ]
        return []


class Fischl(CharactorBase):
    name: Literal['Fischl']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Fischl, Prinzessin der Verurteilung!" Fischl'''
    element: ElementType = ElementType.ELECTRO
    hp: int = 10
    max_hp: int = 10
    charge: int = 0
    max_charge: int = 3
    skills: list[
        PhysicalNormalAttackBase | Nightrider | MidnightPhantasmagoria
    ] = []
    faction: list[FactionType] = [
        FactionType.MONDSTADT,
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # type: ignore
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Bolts of Downfall',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Nightrider(),
            MidnightPhantasmagoria(),
        ]
