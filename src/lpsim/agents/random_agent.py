import numpy as np
from .agent_base import AgentBase
from ..server.match import Match
from ..server.interaction import (
    Responses,
    SwitchCardRequest, SwitchCardResponse,
    ChooseCharactorRequest, ChooseCharactorResponse,
    RerollDiceRequest, RerollDiceResponse,
    DeclareRoundEndResponse,
    ElementalTuningRequest, ElementalTuningResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    UseSkillRequest, UseSkillResponse,
    UseCardRequest, UseCardResponse,
)
from ..server.consts import DieColor


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
                self.random_seed = np.random.randint(0, 2 ** 31 - 1)
            self._random_state.seed(self.random_seed)
            self.random_state_set = True
        return self._random_state.rand()

    def generate_response(self, match: Match) -> Responses | None:
        req_names = list(set([x.name for x in match.requests 
                              if x.player_idx == self.player_idx]))
        if len(req_names) == 0:
            return None
        req_name = req_names[int(self.random() * len(req_names))]
        reqs = [x for x in match.requests
                if x.player_idx == self.player_idx and x.name == req_name]
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
        elif req.name == 'UseCardRequest':
            return self.resp_use_card(req)
        else:
            raise ValueError(f'Unknown request name: {req.name}')

    def resp_switch_card(self, req: SwitchCardRequest) -> SwitchCardResponse:
        """
        Randomly choose a subset of cards.
        """
        card_idxs = []
        for i in range(len(req.card_names)):
            if self.random() < 0.5:
                card_idxs.append(i)
        return SwitchCardResponse(
            request = req, card_idxs = card_idxs
        )

    def resp_choose_charactor(
            self, req: ChooseCharactorRequest) -> ChooseCharactorResponse:
        """
        Randomly choose a charactor.
        """
        return ChooseCharactorResponse(
            request = req, 
            charactor_idx = req.available_charactor_idxs[
                int(self.random() * len(req.available_charactor_idxs))
            ]
        )

    def resp_reroll_dice(self, req: RerollDiceRequest) -> RerollDiceResponse:
        """
        Randomly choose a subset of dice.
        """
        reroll_dice_idxs = []
        for i in range(len(req.colors)):
            if self.random() < 0.5:
                reroll_dice_idxs.append(i)
        return RerollDiceResponse(
            request = req, reroll_dice_idxs = reroll_dice_idxs
        )

    def resp_elemental_tuning(
            self, req: ElementalTuningRequest) -> ElementalTuningResponse:
        """
        Randomly choose a subset of dice.
        """
        return ElementalTuningResponse(
            request = req, 
            dice_idx = req.dice_idxs[
                int(self.random() * len(req.dice_idxs))
            ],
            card_idx = req.card_idxs[
                int(self.random() * len(req.card_idxs))
            ]
        )

    def resp_switch_charactor(
            self, req: SwitchCharactorRequest) -> SwitchCharactorResponse:
        """
        Randomly choose a charactor.
        """
        assert req.cost.any_dice_number <= 1
        idxs = []
        if req.cost.any_dice_number == 1:
            idxs = [int(self.random() * len(req.dice_colors))]
        return SwitchCharactorResponse(
            request = req, 
            dice_idxs = idxs,
        )

    def resp_use_skill(
            self, req: UseSkillRequest) -> UseSkillResponse:
        """
        Randomly choose dice to use skill.
        """
        cost = req.cost
        ele_dice_idxs = [num for num, color in enumerate(req.dice_colors)
                         if color == cost.elemental_dice_color
                         or color == DieColor.OMNI]
        other_dice_idxs = [x for x in range(len(req.dice_colors))
                           if x not in ele_dice_idxs]
        selected = []
        for _ in range(cost.elemental_dice_number):
            if len(ele_dice_idxs) > 0:
                idx = int(self.random() * len(ele_dice_idxs))
                selected.append(ele_dice_idxs.pop(idx))
            else:
                raise ValueError('Not enough elemental dice')
        other_dice_idxs += ele_dice_idxs
        for _ in range(cost.any_dice_number):
            if len(other_dice_idxs) > 0:
                idx = int(self.random() * len(other_dice_idxs))
                selected.append(other_dice_idxs.pop(idx))
            else:
                raise ValueError('Not enough dice')
        selected.sort()

        return UseSkillResponse(
            request = req, 
            dice_idxs = selected
        )

    def resp_use_card(
            self, req: UseCardRequest) -> UseCardResponse:
        """
        Randomly choose dice to use card.
        """
        cost = req.cost
        ele_dice_idxs = [num for num, color in enumerate(req.dice_colors)
                         if color == cost.elemental_dice_color
                         or color == DieColor.OMNI]
        other_dice_idxs = [x for x in range(len(req.dice_colors))
                           if x not in ele_dice_idxs]
        selected = []
        for _ in range(cost.elemental_dice_number):
            if len(ele_dice_idxs) > 0:
                idx = int(self.random() * len(ele_dice_idxs))
                selected.append(ele_dice_idxs.pop(idx))
            else:
                raise ValueError('Not enough elemental dice')
        if cost.same_dice_number > 0:
            color_map = {}
            for color in req.dice_colors:
                if color not in color_map:
                    color_map[color] = 0
                color_map[color] += 1
            keys = list(color_map.keys())
            keys.sort()
            if DieColor.OMNI not in color_map:
                color_map[DieColor.OMNI] = 0
            available_keys = []
            for k in keys:
                v = color_map[k]
                if v >= cost.same_dice_number:
                    available_keys.append(k)
                elif (k != DieColor.OMNI 
                      and v + color_map[DieColor.OMNI] 
                      >= cost.same_dice_number):
                    available_keys.append(k)
            if len(available_keys) > 0:
                k = available_keys[int(self.random() * len(available_keys))]
                other_dice_idxs = []
                ele_dice_idxs = []
                for i, color in enumerate(req.dice_colors):
                    if color == k or color == DieColor.OMNI:
                        if len(selected) < cost.same_dice_number:
                            selected.append(i)
                        else:
                            other_dice_idxs.append(i)
                    else:
                        other_dice_idxs.append(i)
        other_dice_idxs += ele_dice_idxs
        for _ in range(cost.any_dice_number):
            if len(other_dice_idxs) > 0:
                idx = int(self.random() * len(other_dice_idxs))
                selected.append(other_dice_idxs.pop(idx))
            else:
                raise ValueError('Not enough dice')
        selected.sort()

        target = None
        if len(req.targets):
            target = req.targets[
                int(self.random() * len(req.targets))
            ]

        return UseCardResponse(
            request = req, 
            dice_idxs = selected,
            target = target,
        )
