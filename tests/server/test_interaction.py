from src.lpsim.server.consts import DieColor, ObjectPositionType
from src.lpsim.server.deck import Deck
from src.lpsim.server.interaction import (
    SwitchCardRequest, SwitchCardResponse,
    RerollDiceRequest, RerollDiceResponse,
    SwitchCharactorRequest, SwitchCharactorResponse,
    UseCardRequest, UseCardResponse,
    UseSkillRequest, UseSkillResponse,
)
from src.lpsim.server.match import Match
from src.lpsim.server.struct import Cost, ObjectPosition


def test_response_is_valid():
    # mini fake match
    match = Match()
    deck = Deck.from_str('charactor:Nahida')
    match.player_tables[0].charactors.append(deck.charactors[0])
    match.player_tables[1].charactors.append(deck.charactors[0])
    match.player_tables[0].active_charactor_idx = 0
    match.player_tables[1].active_charactor_idx = 0
    req = SwitchCharactorRequest(
        player_idx = 0,
        active_charactor_idx = 0,
        target_charactor_idx = 1,
        dice_colors = [DieColor.CRYO, DieColor.PYRO],
        cost = Cost(
            any_dice_number = 1,
        )
    )
    resp = SwitchCharactorResponse(
        request = req,
        dice_idxs = [0],
    )
    assert resp.is_valid(match)
    resp.dice_idxs = []
    assert not resp.is_valid(match)
    resp.dice_idxs = [-1]
    assert not resp.is_valid(match)
    resp.dice_idxs = [0, 1]
    assert not resp.is_valid(match)
    resp.dice_idxs = [5]
    assert not resp.is_valid(match)
    resp.dice_idxs = []
    resp.request.cost.any_dice_number = 0
    assert resp.is_valid(match)
    req = RerollDiceRequest(
        player_idx = 0,
        colors = [DieColor.CRYO, DieColor.PYRO, DieColor.PYRO, DieColor.PYRO],
        reroll_times = 1,
    )
    resp = RerollDiceResponse(
        request = req,
        reroll_dice_idxs = [0, 1],
    )
    assert resp.is_valid(match)
    resp.reroll_dice_idxs = [0, 0]
    assert not resp.is_valid(match)
    resp.reroll_dice_idxs = [-1, 0]
    assert not resp.is_valid(match)
    resp.reroll_dice_idxs = [0, 4]
    assert not resp.is_valid(match)
    req = SwitchCardRequest(
        player_idx = 0,
        card_names = ['A', 'B', 'A', 'B', 'C'],
        maximum_switch_number = 2,
    )
    resp = SwitchCardResponse(
        request = req,
        card_idxs = [0, 1],
    )
    assert resp.is_valid(match)
    resp.card_idxs = [0, 0]
    assert not resp.is_valid(match)
    resp.card_idxs = [-1, 0]
    assert not resp.is_valid(match)
    resp.card_idxs = [0, 5]
    assert not resp.is_valid(match)
    resp.card_idxs = [0, 1, 2, 3]
    assert not resp.is_valid(match)
    req = UseCardRequest(
        player_idx = 0,
        card_idx = 0,
        dice_colors = [DieColor.CRYO, DieColor.PYRO, DieColor.PYRO, 
                       DieColor.PYRO],
        targets = [],
        cost = Cost(
            same_dice_number = 2,
        )
    )
    resp = UseCardResponse(
        request = req,
        dice_idxs = [1, 2],
        target = None
    )
    assert resp.is_valid(match)
    resp.dice_idxs = [1, 1]
    assert not resp.is_valid(match)
    resp.dice_idxs = [-1, 1]
    assert not resp.is_valid(match)
    resp.dice_idxs = [1, 5]
    assert not resp.is_valid(match)
    resp.dice_idxs = [1, 2, 3]
    assert not resp.is_valid(match)
    resp.dice_idxs = [1, 2]
    target = ObjectPosition(
        player_idx = 0,
        area = ObjectPositionType.HAND,
        id = -1,
    )
    req.targets.append(target)
    assert not resp.is_valid(match)
    req.targets.clear()
    resp.target = target
    assert not resp.is_valid(match)
    req.targets.append(target)
    assert resp.is_valid(match)
    resp.target = resp.target.set_id(321)
    assert not resp.is_valid(match)
    req = UseSkillRequest(
        player_idx = 0,
        charactor_idx = 2,
        skill_idx = 1,
        dice_colors = [DieColor.CRYO, DieColor.PYRO, DieColor.PYRO, 
                       DieColor.PYRO],
        cost = Cost(
            elemental_dice_number = 1,
            elemental_dice_color = DieColor.CRYO,
            any_dice_number = 1,
        )
    )
    resp = UseSkillResponse(
        request = req,
        dice_idxs = [0, 2],
    )
    assert resp.is_valid(match)
    resp.dice_idxs = []
    assert not resp.is_valid(match)
    resp.dice_idxs = [-1, 3]
    assert not resp.is_valid(match)
    resp.dice_idxs = [0, 0]
    assert not resp.is_valid(match)
    resp.dice_idxs = [0, 5]
    assert not resp.is_valid(match)
    resp.dice_idxs = [0, 1, 2]
    assert not resp.is_valid(match)
    resp.dice_idxs = [1, 2]
    assert not resp.is_valid(match)


if __name__ == '__main__':
    test_response_is_valid()
