import logging
from typing import Tuple, List, Literal

from .agent_base import AgentBase
from .random_agent import RandomAgent
from ..server.match import Match
from ..server.interaction import (
    Requests, Responses,
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
    DeclareRoundEndRequest, DeclareRoundEndResponse,
    ElementalTuningRequest, ElementalTuningResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    UseSkillRequest, UseSkillResponse,
    UseCardRequest, UseCardResponse,
)
from ..server.consts import DieColor
from ..server.dice import Dice


class InteractionAgent_V1_0(AgentBase):
    """
    Agent that read inputs interactively, and generate responses.
    All idx are start with 0.

    NOT THE NEWSET VERSION, ONLY FOR COMPATIBILITY.

    Command format and sample:
        sw_card: used to switch cards, with variable length of card indices.
            sample: sw_card 0 1 2
        choose: used to choose charactor, with one charactor idx.
            sample: choose 0
        reroll: used to reroll dice, with variable length of dice indices.
            sample: reroll 0 1 2
        end: used to declare round end, with no args.
            sample: end
        tune: used to elemental tuning, with one dice color and one card idx.
            sample: tune pyro 0
        sw_char: used to switch charactor, with one charactor idx and variable
                length of cost colors.
            sample: sw_char 0 pyro
        skill: used to use skill, with one skill idx and variable length of
                cost colors. skill idx is the index of the skill in the
                available requests.
            sample: skill 0 omni hydro geo
        card: used to use card, with one card idx, one target idx and variable
                length of cost colors. card idx is the index of the card in the
                available requests. target idx is the index of the target in
                the targets of requests, if no targets is needed, target idx
                can be any number.
            sample: card 0 0 omni geo

    Args:
        player_idx: The player idx of the agent.
        version: The version of the agent.
        _cmd_to_name: A dict that maps command to request name.
        verbose_level: The verbose level of the agent, higher means more
            verbose, 0 means no verbose. in level 1, when generate response,
            request names are shown. in level 2, when generate response,
            json of requests are shown.
        available_reqs: The available requests of the agent. Will be updated
            when generate response.
        commands: The commands of the agent. If it is not empty, when get
            command, it will be used instead of input.
        random_after_no_command: If True, when no command, generate random
            response by RandomAgent.
    """
    version: Literal['1.0']
    _cmd_to_name = {
        'sw_card': 'SwitchCardRequest',
        'choose': 'ChooseCharactorRequest',
        'reroll': 'RerollDiceRequest',
        'end': 'DeclareRoundEndRequest',
        'tune': 'ElementalTuningRequest',
        'sw_char': 'SwitchCharactorRequest',
        'skill': 'UseSkillRequest',
        'card': 'UseCardRequest',
    }
    verbose_level: int = 0
    available_reqs: List[Requests] = []

    commands: List[str] = []
    only_use_command: bool = False

    random_after_no_command: bool = False
    random_agent: RandomAgent = RandomAgent(player_idx = -1)

    def _print_requests(self):
        if self.verbose_level == 2:
            print('available requests:')
            for i, req in enumerate(self.available_reqs):
                print(f'{i}: {req.name} {req.json()}')
            return
        print(f'available requests: {[x.name for x in self.available_reqs]}')

    def _get_input(self) -> str:
        if len(self.commands) > 0:
            cmd = self.commands[0]
            self.commands = self.commands[1:]
            logging.info(f'InteractionAgent {self.player_idx}: {cmd}')
            return cmd
        if self.only_use_command:
            return 'no_command'
        print(f'InteractionAgent {self.player_idx}: ')
        return input()

    def _get_cmd(self) -> Tuple[str, List[str]]:
        while True:
            i = self._get_input().strip().split(' ')
            if len(i) == 0:
                continue
            cmd = i[0]
            if cmd == 'help':
                print(f'available commands: {list(self._cmd_to_name.keys())}')
            elif cmd == 'no_command':
                return 'no_command', []
            elif cmd == 'print':
                self._print_requests()
            elif cmd == 'verbose':
                if len(i) == 1:
                    print(f'current verbose level: {self.verbose_level}')
                else:
                    self.verbose_level = int(i[1])
                    print(f'set verbose level to {self.verbose_level}')
            elif cmd in self._cmd_to_name:
                return self._cmd_to_name[cmd], i[1:]
            else:
                try:
                    cmd_num = int(cmd)
                    if cmd_num < 0 or cmd_num >= len(self.available_reqs):
                        print('invalid command number')
                        if self.only_use_command:
                            raise AssertionError()
                        continue
                    return self.available_reqs[cmd_num].name, i[1:]
                except ValueError:
                    print('invalid command')
                    if self.only_use_command:
                        raise AssertionError()
                    continue

    def _colors_to_idx(self, color_names: List[str], 
                       all: List[DieColor]) -> List[int]:
        res: List[int] = []
        selected = [DieColor[x.upper()] for x in color_names]
        all_e: List[DieColor | None] = list(all)
        for x in selected:
            res.append(all_e.index(x))
            all_e[all_e.index(x)] = None
        return res

    def generate_response(self, match: Match) -> Responses | None:
        if self.random_after_no_command and len(self.commands) == 0:
            self.random_agent.player_idx = self.player_idx
            return self.random_agent.generate_response(match)
        self.available_reqs = [x for x in match.requests
                               if x.player_idx == self.player_idx]
        if len(self.available_reqs) == 0:
            return None
        if self.verbose_level >= 1:
            self._print_requests()
        try:
            req_name, args = self._get_cmd()
            if req_name == 'no_command':
                return None
            reqs = [x for x in self.available_reqs if x.name == req_name]
            if len(reqs) == 0:
                print(f'no such request: {req_name}')
                if self.only_use_command:
                    raise AssertionError()
                return self.generate_response(match)
            if req_name == 'SwitchCardRequest':
                return self.resp_switch_card(args, reqs)  # type: ignore
            if req_name == 'ChooseCharactorRequest':
                return self.resp_choose_charactor(args, reqs)  # type: ignore
            if req_name == 'RerollDiceRequest':
                return self.resp_reroll_dice(args, reqs)  # type: ignore
            if req_name == 'DeclareRoundEndRequest':
                return self.resp_declare_round_end(args, reqs)  # type: ignore
            if req_name == 'ElementalTuningRequest':
                return self.resp_elemental_tuning(args, reqs)  # type: ignore
            if req_name == 'SwitchCharactorRequest':
                return self.resp_switch_charactor(args, reqs)  # type: ignore
            if req_name == 'UseSkillRequest':
                return self.resp_use_skill(args, reqs)  # type: ignore
            if req_name == 'UseCardRequest':
                return self.resp_use_card(args, reqs)  # type: ignore
        except Exception as e:
            print(f'error: {e}')
            if self.only_use_command:
                raise e
            return self.generate_response(match)

    def resp_switch_card(
            self, args: List[str], 
            reqs: List[SwitchCardRequest]) -> SwitchCardResponse:
        """
        args: variable length of card indices.
        """
        assert len(reqs) == 1
        return SwitchCardResponse(
            request = reqs[0], card_idxs = [int(x) for x in args]
        )

    def resp_choose_charactor(
            self, args: List[str], 
            reqs: List[ChooseCharactorRequest]) -> ChooseCharactorResponse:
        """
        args: one charactor idx.
        """
        assert len(reqs) == 1
        return ChooseCharactorResponse(
            request = reqs[0], charactor_idx = int(args[0])
        )

    def resp_reroll_dice(
            self, args: List[str],
            reqs: List[RerollDiceRequest]) -> RerollDiceResponse:
        """
        args: variable length of dice indices.
        """
        assert len(reqs) == 1
        return RerollDiceResponse(
            request = reqs[0], reroll_dice_idxs = [int(x) for x in args]
        )

    def resp_elemental_tuning(
            self, args: List[str],
            reqs: List[ElementalTuningRequest]) -> ElementalTuningResponse:
        """
        args: one dice color and one card idx.
        """
        assert len(reqs) == 1
        dice_idx = self._colors_to_idx(args[:1], reqs[0].dice_colors)[0]
        return ElementalTuningResponse(
            request = reqs[0],
            dice_idx = dice_idx,
            card_idx = int(args[1])
        )

    def resp_switch_charactor(
            self, args: List[str], 
            reqs: List[SwitchCharactorRequest]) -> SwitchCharactorResponse:
        """
        args: one charactor idx and variable length of cost colors.
        """
        cidx = int(args[0])
        selected_req: SwitchCharactorRequest | None = None
        for req in reqs:
            if req.target_charactor_idx == cidx:
                selected_req = req
                break
        assert selected_req is not None
        dice_idxs = self._colors_to_idx(args[1:], reqs[0].dice_colors)
        return SwitchCharactorResponse(
            request = selected_req,
            dice_idxs = dice_idxs
        )

    def resp_declare_round_end(
            self, args: List[str],
            reqs: List[DeclareRoundEndRequest]) -> DeclareRoundEndResponse:
        """
        args: none
        """
        assert len(reqs) == 1
        return DeclareRoundEndResponse(
            request = reqs[0]
        )

    def resp_use_skill(
            self, args: List[str],
            reqs: List[UseSkillRequest]) -> UseSkillResponse:
        """
        args: one skill idx, variable length of cost colors.
        """
        skill_req = reqs[int(args[0])]
        dice_idxs = self._colors_to_idx(args[1:], skill_req.dice_colors)
        return UseSkillResponse(
            request = skill_req,
            dice_idxs = dice_idxs
        )

    def resp_use_card(
            self, args: List[str],
            reqs: List[UseCardRequest]) -> UseCardResponse:
        """
        args: one card idx, one target idx, variable length of cost colors.
        """
        card_req = reqs[int(args[0])]
        target_idx = int(args[1])
        target = None
        if len(card_req.targets) > 0:
            target = card_req.targets[target_idx]
        dice_idxs = self._colors_to_idx(args[2:], card_req.dice_colors)
        return UseCardResponse(
            request = card_req,
            dice_idxs = dice_idxs,
            target = target
        )


class InteractionAgent_V2_0(InteractionAgent_V1_0):
    """
    Thie version changes the command format of tune, card and skill to make 
    easier use. And can use idx of dice to instead die color.
    All idx are start with 0.

    For tune, it will need to input the card idx first, then the dice color. 
    For skill, the skill idx is not the index of the skill in the available
        requests, but the index of the skill in the skills of the active 
        charactor.
    For card, the card idx is not the index of the card in the available 
        requests, but the index of the card in the hand. 

    Changed commands:
        tune: used to elemental tuning, with one card idx and one dice color.
            sample: tune 0 pyro | tune 0 6
        skill: used to use skill, with one skill idx and variable length of
                cost colors. skill idx is the index of the skill of the active
                charactor.
            sample: skill 0 omni hydro geo | skill 2 0 2 3
        card: used to use card, with one card idx, one target idx and variable
                length of cost colors. card idx is the index of the card in 
                hands. target idx is the index of the target in
                the targets of requests, if no targets is needed, target idx
                can be any number.
            sample: card 0 0 omni geo | card 1 0 5 6

    Unchanged commands (but can use idx of dice):
        sw_card: used to switch cards, with variable length of card indices.
            sample: sw_card 0 1 2
        choose: used to choose charactor, with one charactor idx.
            sample: choose 0
        reroll: used to reroll dice, with variable length of dice indices or 
            dice colors.
            sample: reroll 0 1 2 | reroll pyro geo
        end: used to declare round end, with no args.
            sample: end
        sw_char: used to switch charactor, with one charactor idx and variable
                length of cost colors.
            sample: sw_char 0 pyro | sw_char 1 6

    Args:
        Unchanged, please refer to V1.0
    """
    version: Literal['2.0'] = '2.0'

    def _colors_to_idx(self, color_names: List[str], 
                       all: List[DieColor]) -> List[int]:
        try:
            color_idxs = [int(x) for x in color_names]
            # int representation
            return color_idxs
        except ValueError:
            pass
        # color representation
        dice = Dice(colors = all)
        res = dice.colors_to_idx(
            [DieColor(x.upper()) for x in color_names]
        )
        return res

    def resp_reroll_dice(
            self, args: List[str],
            reqs: List[RerollDiceRequest]) -> RerollDiceResponse:
        """
        args: variable length of dice idx or colors
        """
        assert len(reqs) == 1
        dice_idx = self._colors_to_idx(args, reqs[0].colors)
        return RerollDiceResponse(
            request = reqs[0], reroll_dice_idxs = dice_idx
        )

    def resp_elemental_tuning(
            self, args: List[str],
            reqs: List[ElementalTuningRequest]) -> ElementalTuningResponse:
        """
        args: one card idx and dice color.
        """
        assert len(reqs) == 1
        cost_idx = self._colors_to_idx(args[1:], reqs[0].dice_colors)[0]
        return ElementalTuningResponse(
            request = reqs[0],
            dice_idx = cost_idx,
            card_idx = int(args[0])
        )

    def resp_use_skill(
            self, args: List[str],
            reqs: List[UseSkillRequest]) -> UseSkillResponse:
        """
        args: one skill idx, variable length of cost colors.
        """
        skill_reqs = [x for x in reqs if x.skill_idx == int(args[0])]
        assert len(skill_reqs) == 1
        skill_req = skill_reqs[0]
        dice_idxs = self._colors_to_idx(args[1:], skill_req.dice_colors)
        return UseSkillResponse(
            request = skill_req,
            dice_idxs = dice_idxs
        )

    def resp_use_card(
            self, args: List[str],
            reqs: List[UseCardRequest]) -> UseCardResponse:
        """
        args: one card idx, one target idx, variable length of cost colors.
        """
        card_reqs = [x for x in reqs if x.card_idx == int(args[0])]
        assert len(card_reqs) == 1
        card_req = card_reqs[0]
        target_idx = int(args[1])
        target = None
        if len(card_req.targets) > 0:
            target = card_req.targets[target_idx]
        dice_idxs = self._colors_to_idx(args[2:], card_req.dice_colors)
        return UseCardResponse(
            request = card_req,
            dice_idxs = dice_idxs,
            target = target
        )


InteractionAgent = InteractionAgent_V2_0
