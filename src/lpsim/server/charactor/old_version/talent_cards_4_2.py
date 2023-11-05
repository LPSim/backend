"""
All old talent cards that modified in version 4.2 are moved to here.
"""


from typing import Any, List, Literal, Tuple

from ...modifiable_values import CostValue, DamageValue

from ...action import Actions, ChargeAction, CreateObjectAction, MakeDamageAction

from ...event import ReceiveDamageEventArguments, RoundPrepareEventArguments, SkillEndEventArguments

from ...consts import CostLabels, DamageElementalType, DamageType, DieColor, ElementType, ObjectPositionType, PlayerActionLabels, SkillType

from ...struct import Cost, ObjectPosition
from ..charactor_base import SkillTalent, TalentBase


class MirrorCage_3_3(SkillTalent):
    name: Literal['Mirror Cage']
    desc: str = (
        'Combat Action: When your active character is Mirror Maiden, equip '
        'this card. After Mirror Maiden equips this card, immediately use '
        'Influx Blast once. When your Mirror Maiden, who has this card '
        'equipped, creates a Refraction, it will have the following effects: '
        'Starting Duration (Rounds) +1, will increase the Elemental Dice Cost '
        'of switching from a character to which this is attached to another '
        'character by 1.'
    )
    version: Literal['3.3']
    charactor_name: Literal['Mirror Maiden'] = 'Mirror Maiden'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4
    )
    skill: Literal['Influx Blast'] = 'Influx Blast'


class GloriousSeason_3_3(SkillTalent):
    name: Literal['Glorious Season'] = 'Glorious Season'
    desc: str = (
        'Combat Action: When your active character is Barbara, equip this '
        'card. '
        'After Barbara equips this card, immediately use Let the Show Begin♪ '
        'once. When your Barbara, who has this card equipped, is on the '
        'field, Melody Loop will allow you to spend 1 less Elemental Die the '
        'next time you use "Switch Character." (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Barbara'] = 'Barbara'
    cost: Cost = Cost(
        elemental_dice_number = 4,
        elemental_dice_color = DieColor.HYDRO,
    )
    skill: Literal['Let the Show Begin♪'] = 'Let the Show Begin♪'
    usage: int = 1

    def event_handler_ROUND_PREPARE(
        self, match: Any, event_args: RoundPrepareEventArguments
    ) -> List[Actions]:
        """reset usage"""
        self.usage = 1
        return []

    def value_modifier_COST(
        self, value: CostValue, 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        Once per round, if summon "Melody Loop" is valid in our summon area,
        and our do switch, and have cost, then cost -1.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, no effect
            return value
        if self.usage <= 0:
            # no usage, no effect
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTOR == 0:
            # not switch charatctor, no effect
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player, no effect
            return value
        summons = match.player_tables[self.position.player_idx].summons
        have_summon = False
        for summon in summons:
            if summon.name == 'Melody Loop':
                have_summon = True
                break
        if not have_summon:
            # not have summon, no effect
            return value
        # decrease 1 any cost
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value


class AbsorbingPrism_3_7(TalentBase):
    name: Literal['Absorbing Prism']
    desc: str = (
        'Combat Action: When your active character is Electro Hypostasis, '
        'heal that character for 3 HP and attach the Electro Crystal Core to '
        'them.'
    )
    version: Literal['3.7']
    charactor_name: Literal['Electro Hypostasis'] = 'Electro Hypostasis'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3
    )
    remove_when_used: bool = True

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        return PlayerActionLabels.CARD.value, True

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MakeDamageAction | CreateObjectAction]:
        """
        Using this card will heal electro hypostasis by 3 hp and attach
        electro crystal core to it. No need to equip it.
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        assert charactor.name == self.charactor_name
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -3,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = Cost(),
                    )
                ],
            ),
            CreateObjectAction(
                object_name = 'Electro Crystal Core',
                object_position = charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_arguments = {}
            )
        ]


class Crossfire_3_3(SkillTalent):
    name: Literal['Crossfire']
    desc: str = (
        'Combat Action: When your active character is Xiangling, equip this '
        'card. After Xiangling equips this card, immediately use Guoba Attack '
        'once. When your Xiangling, who has this card equipped, uses Guoba '
        'Attack, she will also deal 1 Pyro DMG.'
    )
    version: Literal['3.3']
    charactor_name: Literal['Xiangling'] = 'Xiangling'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4
    )
    skill: Literal['Guoba Attack'] = 'Guoba Attack'


class TheOverflow_3_8(SkillTalent):
    name: Literal['The Overflow']
    desc: str = (
        'Combat Action: When your active character is Candace, equip this '
        'card. After Candace equips this card, immediately use Sacred Rite: '
        "Wagtail's Tide once. When this card is equipped by Candace, her "
        'Prayer of the Crimson Crown has the following extra effect: After '
        'your character uses a Normal Attack: Deals 1 Hydro DMG. (Once per '
        'Round)'
    )
    version: Literal['3.8']
    charactor_name: Literal['Candace'] = 'Candace'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: Literal[
        "Sacred Rite: Wagtail's Tide"
    ] = "Sacred Rite: Wagtail's Tide"


class SteadyBreathing_3_3(SkillTalent):
    name: Literal['Steady Breathing']
    desc: str = (
        'Combat Action: When your active character is Chongyun, equip this '
        "card. After Chongyun equips this card, immediately use Chonghua's "
        'Layered Frost once. When your Chongyun, who has this card equipped, '
        'creates a Chonghua Frost Field, it will have the following effects: '
        'Starting Duration (Rounds) +1, will cause your Sword, Claymore, and '
        "Polearm-wielding characters' Normal Attacks to deal +1 DMG."
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Chongyun'] = 'Chongyun'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4
    )
    skill: Literal["Chonghua's Layered Frost"] = "Chonghua's Layered Frost"
    status_max_usage: int = 3


class NaganoharaMeteorSwarm_3_3(SkillTalent):
    name: Literal['Naganohara Meteor Swarm']
    desc: str = (
        'Combat Action: When your active character is Yoimiya, equip this '
        'card. After Yoimiya equips this card, immediately use Niwabi '
        'Fire-Dance once. After your Yoimiya, who has this card equipped, '
        'triggers Niwabi Enshou: Deal 1 additional Pyro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Yoimiya'] = 'Yoimiya'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 2,
    )
    skill: Literal['Niwabi Fire-Dance'] = 'Niwabi Fire-Dance'
    status_max_usage: int = 2


class Awakening_3_3(SkillTalent):
    name: Literal['Awakening']
    desc: str = (
        'Combat Action: When your active character is Razor, equip this card. '
        'After Razor equips this card, immediately use Claw and Thunder once. '
        'After your Razor, who has this card equipped, uses Claw and Thunder: '
        '1 of your Electro characters gains 1 Energy. '
        '(Active Character prioritized)'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Razor'] = 'Razor'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4
    )
    skill: Literal['Claw and Thunder'] = 'Claw and Thunder'
    usage: int = 999
    max_usage: int = 999

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        reset usage
        """
        self.usage = self.max_usage
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        If equipped and use elemental skill, charge one of our electro 
        charactor
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not equipped, or this charactor use skill
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        # find charge target
        table = match.player_tables[self.position.player_idx]
        charactors = table.charactors
        active = charactors[table.active_charactor_idx]
        target_idx = -1
        if (
            active.element == ElementType.ELECTRO
            and active.charge < active.max_charge
        ):
            # active electro and not full charge
            target_idx = table.active_charactor_idx
        else:
            # check other charactors
            for chraractor_idx, charactor in enumerate(charactors):
                if (
                    charactor.element == ElementType.ELECTRO
                    and charactor.charge < charactor.max_charge
                    and charactor.is_alive
                ):
                    target_idx = chraractor_idx
                    break
        if target_idx == -1:
            # no target
            return []
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        # charge target
        return [ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = target_idx,
            charge = 1
        )]


class LightningStorm_3_4(SkillTalent):
    name: Literal['Lightning Storm']
    desc: str = (
        'Combat Action: When your active character is Beidou, equip this '
        'card. After Beidou equips this card, immediately use Tidecaller '
        'once. When Beidou, who has this card equipped, uses Wavestrider: '
        "If DMG is taken while Prepare Skill is active, Beidou's Normal "
        "Attacks this Round will cost 1 less Unaligned Element. "
        '(Can be triggered 2 times)'
    )
    version: Literal['3.4'] = '3.4'
    charactor_name: Literal['Beidou'] = 'Beidou'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Tidecaller'] = 'Tidecaller'

    usage: int = 2
    max_usage: int = 2
    activated: bool = False
    need_to_activate: bool = True

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        reset usage and activate
        """
        self.usage = self.max_usage
        self.activated = False
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self receive damage and has status, activate
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        if not event.final_damage.is_corresponding_charactor_receive_damage(
            self.position, match,
        ):
            # not corresponding charactor
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        for status in charactor.status:
            if status.name == 'Tidecaller: Surf Embrace':
                self.activated = True
                break
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        If activated, decrease self normal attack cost by 1
        """
        if not self.activated and self.need_to_activate:
            # not activated and need to activate
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR,
        ):
            # not self skill
            return value
        if value.cost.label & CostLabels.NORMAL_ATTACK.value == 0:
            # not normal attack
            return value
        if self.usage <= 0:
            # no usage
            return value
        # decrease
        if value.cost.decrease_cost(None):  # pragma: no branch
            if mode == 'REAL':
                self.usage -= 1
        return value


class SinOfPride_3_5(SkillTalent):
    name: Literal['Sin of Pride']
    desc: str = (
        'Combat Action: When your active character is Kujou Sara, equip this '
        'card. After Kujou Sara equips this card, immediately use '
        'Subjugation: Koukou Sendou once. When Kujou Sara is active and has '
        'this card equipped, all allied Electro characters with Crowfeather '
        'Cover will deal +1 additional Elemental Skill and Elemental Burst '
        'DMG.'
    )
    version: Literal['3.5'] = '3.5'
    charactor_name: Literal['Kujou Sara'] = 'Kujou Sara'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: Literal['Subjugation: Koukou Sendou'] = 'Subjugation: Koukou Sendou'


class FeatherfallJudgment_3_3(SkillTalent):
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
    skill: Literal[
        'Secret Rite: Chasmic Soulfarer'
    ] = 'Secret Rite: Chasmic Soulfarer'
    active_levels: List[int] = [3, 5]


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


class BunnyTriggered_3_7(SkillTalent):
    name: Literal['Bunny Triggered']
    desc: str = (
        'Combat Action: When your active character is Amber, equip this card. '
        'After Amber equips this card, immediately use Explosive Puppet once. '
        'After you use a Normal Attack: If this card and Baron Bunny are '
        'still on the field, then Baron Bunny explodes and deals 3 Pyro DMG.'
    )
    version: Literal['3.7'] = '3.7'
    charactor_name: Literal['Amber'] = 'Amber'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )
    skill: Literal['Explosive Puppet'] = 'Explosive Puppet'
    damage: int = 3
