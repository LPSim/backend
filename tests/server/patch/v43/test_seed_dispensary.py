import os
from src.lpsim import MatchState
from tests.utils_for_test import (
    get_test_id_from_command, make_respond, set_16_omni, read_from_log_json
)


def test_seed_dispensary():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), 
                     'jsons', 
                     'test_seed_dispensary.json')
    )
    # modify hp
    for i in range(2):
        charactors = match.player_tables[i].player_deck_information.charactors
        for c in charactors:
            c.hp = c.max_hp = 30
    # add omnipotent guide
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_seed_dispensary()
