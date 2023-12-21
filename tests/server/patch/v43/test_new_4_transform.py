import os
from src.lpsim import MatchState
from tests.utils_for_test import (
    get_pidx_cidx, get_test_id_from_command, make_respond, set_16_omni, 
    read_from_log_json
)


def test_new_4_tranform():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), 
                     'jsons', 
                     'test_new_4_transform.json')
    )
    # add omnipotent guide
    set_16_omni(match)
    match.start()
    match.step()
    new_commands = [[], []]
    while True:
        if match.need_respond(0):
            agent = agent_0
            nc = new_commands[0]
        elif match.need_respond(1):
            agent = agent_1
            nc = new_commands[1]
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            nc.append(agent.commands[0])
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 10:
                pidx, cidx = get_pidx_cidx(cmd)
                desc = match.player_tables[pidx].charactors[cidx].desc
                cmd_desc = ' '.join(cmd[3:])[1:-1]
                assert desc == cmd_desc
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_new_4_tranform()
