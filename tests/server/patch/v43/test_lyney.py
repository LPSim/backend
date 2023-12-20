import os
from src.lpsim import MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_test_id_from_command, 
    make_respond, set_16_omni, read_from_log_json
)


def test_lyney():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), 'jsons', 'test_lyney.json')
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
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                # a sample of HP check based on the command string.
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].summons, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_lyney()
