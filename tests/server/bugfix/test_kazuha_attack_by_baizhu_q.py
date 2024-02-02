import os
from lpsim import MatchState
from tests.utils_for_test import (
    check_hp,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
    read_from_log_json,
)


def test_kazuha_attack_by_baizhu_q():
    json_fname = "test_kazuha_attack_by_baizhu_q.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    match, agent_0, agent_1 = read_from_log_json(json_path)
    match.config.history_level = 0
    # modify hp
    # for i in range(2):
    #     characters = match.player_tables[i].player_deck_information.characters  # noqa: E501
    #     for c in characters:
    #         c.hp = c.max_hp = 30
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
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_kazuha_attack_by_baizhu_q()
