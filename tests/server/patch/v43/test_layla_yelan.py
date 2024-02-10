import os
from lpsim import MatchState
from tests.utils_for_test import (
    check_hp,
    check_usage,
    get_pidx_cidx,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
    read_from_log_json,
)


def test_layla_yelan():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), "jsons", "test_layla_yelan.json")
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
            raise AssertionError("No need respond.")
        # do tests
        while True:
            nc.append(agent.commands[0])
            cmd = agent.commands[0].strip().split(" ")
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].summons, cmd[3:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[3:])
            elif test_id == 4:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[3:])
            elif test_id == 5:
                pidx, cidx = get_pidx_cidx(cmd)
                check_usage(match.player_tables[pidx].characters[cidx].status, cmd[3:])
            elif test_id == 6:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[3])
            elif test_id == 8:
                pidx, cidx = get_pidx_cidx(cmd)
                character = match.player_tables[pidx].characters[cidx]
                ele_app = character.element_application
                assert len(ele_app) == 0
                assert len(cmd[4:]) == 0
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_layla_yelan()
