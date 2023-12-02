from typing import Any, Literal, List

from ....utils.class_registry import register_class

from ...event import CreateObjectEventArguments

from ...action import Actions, ChangeObjectUsageAction, CreateObjectAction

from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, ObjectPositionType, WeaponType
)

from ..charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalNormalAttackBase, 
    ElementalSkillBase, SkillTalent
)


class AllSchemesToKnow(ElementalSkillBase):
    name: Literal['All Schemes to Know'] = 'All Schemes to Know'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = []
        damage_ret = super().get_actions(match)
        # get target charactors and active charactor.
        player_idx = self.position.player_idx
        target_table = match.player_tables[1 - player_idx]
        target_charactors = target_table.charactors
        target_active_charactor = target_charactors[
            target_table.active_charactor_idx]
        # default set status to active charactor
        position = target_active_charactor.position.set_area(
            ObjectPositionType.CHARACTOR_STATUS)
        ret.append(
            CreateObjectAction(
                object_name = 'Seed of Skandha',
                object_position = position,
                object_arguments = {},
            )
        )
        # get seed of skandha status.
        active_charactor_status_names = [
            x.name for x in target_active_charactor.status
        ]
        if 'Seed of Skandha' in active_charactor_status_names:
            # apply to all opposing charactors.
            for charactor in target_charactors:
                if charactor.is_defeated:
                    continue
                if charactor.id != target_active_charactor.id:
                    position = charactor.position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS)
                    ret.append(
                        CreateObjectAction(
                            object_name = 'Seed of Skandha',
                            object_position = position,
                            object_arguments = {},
                        )
                    )
        # apply damage after apply status.
        ret += damage_ret
        return ret


class AllSchemesToKnowTathata(ElementalSkillBase):
    name: Literal[
        'All Schemes to Know: Tathata'
    ] = 'All Schemes to Know: Tathata'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 5,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret: List[Actions] = []
        damage_ret = super().get_actions(match)
        # get target charactors and active charactor.
        player_idx = self.position.player_idx
        target_table = match.player_tables[1 - player_idx]
        target_charactors = target_table.charactors
        # apply to all opposing charactors.
        for charactor in target_charactors:
            if charactor.is_defeated:
                continue
            position = charactor.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS)
            ret.append(
                CreateObjectAction(
                    object_name = 'Seed of Skandha',
                    object_position = position,
                    object_arguments = {},
                )
            )
        ret += damage_ret
        return ret


class IllusoryHeart(ElementalBurstBase):
    name: Literal['Illusory Heart'] = 'Illusory Heart'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_team_status('Shrine of Maya'))
        return ret


class TheSeedOfStoredKnowledge_3_7(SkillTalent):
    """
    Three effects are implemented in different places:
        Pyro: when Seed of Skandha is triggered, it will check whether need
            to add dendro damage.
        Electro: when Shrine of Maya is summoned, the status will check whether
            need to add one usage to Seed of Skandha.
        Hydro: when Shrine of Maya is summoned, this talent card will try
            to add one usage if is equipped.
    """
    name: Literal[
        'The Seed of Stored Knowledge'
    ] = 'The Seed of Stored Knowledge'
    charactor_name: Literal['Nahida'] = 'Nahida'
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2,
    )
    skill: Literal['Illusory Heart'] = 'Illusory Heart'

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[ChangeObjectUsageAction]:
        """
        when Shrine of Maya is summoned, if this card is equipped, add one
        usage.
        """
        if event.action.object_name != 'Shrine of Maya':
            # not creating Shrine of Maya, do nothing.
            return []
        if not self.position.check_position_valid(
            event.action.object_position, match, player_idx_same = True,
            source_area = ObjectPositionType.CHARACTOR,
            source_is_active_charactor = True,
        ):
            # not self, or not equipped, or not active charactor, do nothing.
            return []
        table = match.player_tables[self.position.player_idx]
        has_hydro_charactor = False
        for charactor in table.charactors:
            if charactor.element == ElementType.HYDRO:
                has_hydro_charactor = True
                break
        if not has_hydro_charactor:
            # no hydro charactor, do nothing.
            return []
        team_status = table.team_status
        for status in team_status:
            if status.name == 'Shrine of Maya':
                # has Shrine Of Maya, add one usage.
                return [ChangeObjectUsageAction(
                    object_position = status.position,
                    change_usage = 1,
                )]
        raise AssertionError('Shrine of Maya not found.')


class Nahida_3_7(CharactorBase):
    name: Literal['Nahida']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | AllSchemesToKnow | AllSchemesToKnowTathata
        | IllusoryHeart
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU,
    ]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Akara',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            AllSchemesToKnow(),
            AllSchemesToKnowTathata(),
            IllusoryHeart(),
        ]


register_class(Nahida_3_7 | TheSeedOfStoredKnowledge_3_7)
