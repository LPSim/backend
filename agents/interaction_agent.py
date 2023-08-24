import logging
from typing import Tuple, List
from .agent_base import AgentBase
from .random_agent import RandomAgent
from server.match import Match
from server.interaction import (
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
from server.consts import DieColor


class InteractionAgent(AgentBase):
    """
    Agent that read inputs interactively, and generate responses.

    Args:
        player_id: The player id of the agent.
        _cmd_to_name: A dict that maps command to request name.
        verbose_level: The verbose level of the agent, higher means more
            verbose, 0 means no verbose. in level 1, when generate response,
            request names are shown. in level 2, when generate response,
            json of requests are shown. TODO: use __repr__?
        available_reqs: The available requests of the agent. Will be updated
            when generate response.
        commands: The commands of the agent. If it is not empty, when get
            command, it will be used instead of input.
        random_after_no_command: If True, when no command, generate random
            response by RandomAgent.
    """
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
    random_agent: RandomAgent = RandomAgent(player_id = -1)

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
            logging.info(f'InteractionAgent {self.player_id}: {cmd}')
            return cmd
        if self.only_use_command:
            return 'no_command'
        print(f'InteractionAgent {self.player_id}: ')
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
                        continue
                    return self.available_reqs[cmd_num].name, i[1:]
                except ValueError:
                    print('invalid command')
                    continue               

    def _colors_to_ids(self, color_names: List[str], 
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
            self.random_agent.player_id = self.player_id
            return self.random_agent.generate_response(match)
        self.available_reqs = [x for x in match.requests
                               if x.player_id == self.player_id]
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
            return self.generate_response(match)

    def resp_switch_card(
            self, args: List[str], 
            reqs: List[SwitchCardRequest]) -> SwitchCardResponse:
        """
        args: variable length of card ids.
        """
        assert len(reqs) == 1
        return SwitchCardResponse(
            request = reqs[0], card_ids = [int(x) for x in args]
        )

    def resp_choose_charactor(
            self, args: List[str], 
            reqs: List[ChooseCharactorRequest]) -> ChooseCharactorResponse:
        """
        args: one charactor id.
        """
        assert len(reqs) == 1
        return ChooseCharactorResponse(
            request = reqs[0], charactor_id = int(args[0])
        )

    def resp_reroll_dice(
            self, args: List[str],
            reqs: List[RerollDiceRequest]) -> RerollDiceResponse:
        """
        args: variable length of dice ids.
        """
        assert len(reqs) == 1
        return RerollDiceResponse(
            request = reqs[0], reroll_dice_ids = [int(x) for x in args]
        )

    def resp_elemental_tuning(
            self, args: List[str],
            reqs: List[ElementalTuningRequest]) -> ElementalTuningResponse:
        """
        args: one dice color and one card id.
        """
        assert len(reqs) == 1
        cost_id = self._colors_to_ids(args[:1], reqs[0].dice_colors)[0]
        return ElementalTuningResponse(
            request = reqs[0],
            cost_id = cost_id,
            card_id = int(args[1])
        )

    def resp_switch_charactor(
            self, args: List[str], 
            reqs: List[SwitchCharactorRequest]) -> SwitchCharactorResponse:
        """
        args: one charactor id and variable length of cost colors.
        """
        assert len(reqs) == 1
        cost_ids = self._colors_to_ids(args[1:], reqs[0].dice_colors)
        return SwitchCharactorResponse(
            request = reqs[0],
            charactor_id = int(args[0]),
            cost_ids = cost_ids
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
        cost_ids = self._colors_to_ids(args[1:], skill_req.dice_colors)
        return UseSkillResponse(
            request = skill_req,
            cost_ids = cost_ids
        )

    def resp_use_card(
            self, args: List[str],
            reqs: List[UseCardRequest]) -> UseCardResponse:
        """
        args: one card idx, variable length of cost colors.
        """
        card_req = reqs[int(args[0])]
        cost_ids = self._colors_to_ids(args[1:], card_req.dice_colors)
        return UseCardResponse(
            request = card_req,
            cost_ids = cost_ids
        )
