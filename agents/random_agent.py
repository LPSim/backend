import numpy as np
from .agent_base import AgentBase
from server.match import Match
from server.interaction import (
    Responses,
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
    DeclareRoundEndResponse,
    ElementalTuningRequest, ElementalTuningResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    UseSkillRequest, UseSkillResponse,
)
from server.consts import DieColor


class RandomAgent(AgentBase):
    """
    Agent that randomly choose one type of requests, randomly choose one of 
    selected type, and randomly choose one of available options.
    """
    random_seed: int | None = None
    _random_state: np.random.RandomState = np.random.RandomState()
    random_state_set: bool = False

    def random(self) -> float:
        """
        Return a random float between 0 and 1.
        """
        if not self.random_state_set:
            if self.random_seed is None:
                self.random_seed = np.random.randint(0, 2 ** 32 - 1)
            self._random_state.seed(self.random_seed)
            self.random_state_set = True
        return self._random_state.rand()

    def generate_response(self, match: Match) -> Responses | None:
        req_names = list(set([x.name for x in match.requests 
                              if x.player_id == self.player_id]))
        if len(req_names) == 0:
            return None
        req_name = req_names[int(self.random() * len(req_names))]
        reqs = [x for x in match.requests
                if x.player_id == self.player_id and x.name == req_name]
        req = reqs[int(self.random() * len(reqs))]

        if req.name == 'SwitchCardRequest':
            return self.resp_switch_card(req)
        elif req.name == 'ChooseCharactorRequest':
            return self.resp_choose_charactor(req)
        elif req.name == 'RerollDiceRequest':
            return self.resp_reroll_dice(req)
        elif req.name == 'DeclareRoundEndRequest':
            return DeclareRoundEndResponse(
                request = req
            )
        elif req.name == 'ElementalTuningRequest':
            return self.resp_elemental_tuning(req)
        elif req.name == 'SwitchCharactorRequest':
            return self.resp_switch_charactor(req)
        elif req.name == 'UseSkillRequest':
            return self.resp_use_skill(req)
        else:
            raise ValueError(f'Unknown request name: {req.name}')

    def resp_switch_card(self, req: SwitchCardRequest) -> SwitchCardResponse:
        """
        Randomly choose a subset of cards.
        """
        card_ids = []
        for i in range(len(req.card_names)):
            if self.random() < 0.5:
                card_ids.append(i)
        return SwitchCardResponse(
            request = req, card_ids = card_ids
        )

    def resp_choose_charactor(
            self, req: ChooseCharactorRequest) -> ChooseCharactorResponse:
        """
        Randomly choose a charactor.
        """
        return ChooseCharactorResponse(
            request = req, 
            charactor_id = req.available_charactor_ids[
                int(self.random() * len(req.available_charactor_ids))
            ]
        )

    def resp_reroll_dice(self, req: RerollDiceRequest) -> RerollDiceResponse:
        """
        Randomly choose a subset of dice.
        """
        reroll_dice_ids = []
        for i in range(len(req.colors)):
            if self.random() < 0.5:
                reroll_dice_ids.append(i)
        return RerollDiceResponse(
            request = req, reroll_dice_ids = reroll_dice_ids
        )

    def resp_elemental_tuning(
            self, req: ElementalTuningRequest) -> ElementalTuningResponse:
        """
        Randomly choose a subset of dice.
        """
        return ElementalTuningResponse(
            request = req, 
            cost_id = req.dice_ids[
                int(self.random() * len(req.dice_ids))
            ],
            card_id = req.card_ids[
                int(self.random() * len(req.card_ids))
            ]
        )

    def resp_switch_charactor(
            self, req: SwitchCharactorRequest) -> SwitchCharactorResponse:
        """
        Randomly choose a charactor.
        """
        return SwitchCharactorResponse(
            request = req, 
            cost_ids = [int(self.random() * len(req.dice_colors))],
            charactor_id = req.candidate_charactor_ids[
                int(self.random() * len(req.candidate_charactor_ids))
            ],
        )

    def resp_use_skill(
            self, req: UseSkillRequest) -> UseSkillResponse:
        """
        Randomly choose dice to use skill.
        """
        cost = req.cost
        ele_dice_ids = [num for num, color in enumerate(req.dice_colors)
                        if color == cost.elemental_dice_color
                        or color == DieColor.OMNI]
        other_dice_ids = [x for x in range(len(req.dice_colors))
                          if x not in ele_dice_ids]
        selected = []
        for _ in range(cost.elemental_dice_number):
            if len(ele_dice_ids) > 0:
                idx = int(self.random() * len(ele_dice_ids))
                selected.append(ele_dice_ids.pop(idx))
            else:
                raise ValueError('Not enough elemental dice')
        other_dice_ids += ele_dice_ids
        for _ in range(cost.any_dice_number):
            if len(other_dice_ids) > 0:
                idx = int(self.random() * len(other_dice_ids))
                selected.append(other_dice_ids.pop(idx))
            else:
                raise ValueError('Not enough dice')
        selected.sort()

        return UseSkillResponse(
            request = req, 
            cost_ids = selected
        )
