import json
import os
from lpsim import MatchState
from tests.utils_for_test import (
    get_test_id_from_command,
    make_respond,
    set_16_omni,
    read_from_log_json,
)


def template():
    json_fname = "sayu.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    match, agent_0, agent_1 = read_from_log_json(json_path)
    # backup json
    open("111.json", "w", encoding="utf8").write(
        open(json_path, "r", encoding="utf8").read()
    )
    json_data = json.loads(open(json_path, "r", encoding="utf8").read())
    if "command_history_raw" in json_data:
        raise AssertionError("command_history_raw already exists!")
    json_data["command_history_raw"] = json_data["command_history"]
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
        # add tests
        enable = [
            1,  # hp
            2,  # summon
            # 3,  # support
            # 4,  # team status
            5,  # character status
            # 6,  # hands
            # 7,  # dice
            # 8,  # charge
            # 9,  # summon element
            # 10,  # character desc
            # 11,  # hand usage availability
            12,  # element application
        ]
        # 1 for hp
        hp_str = "TEST 1"
        for i in range(2):
            for c in match.player_tables[i].characters:
                hp_str += " " + str(c.hp)
        if 1 in enable:
            nc.append(hp_str)
        for tnum, table in enumerate(match.player_tables):
            # 2 for summon usage
            summon_str = f"TEST 2 p{tnum}"
            for s in table.summons:
                summon_str += f" {s.usage}"
            if 2 in enable:
                nc.append(summon_str)
            # 3 for support
            support_str = f"TEST 3 p{tnum}"
            for s in table.supports:
                support_str += f" {s.usage}"
            if 3 in enable:
                nc.append(support_str)
            # 4 for team status
            team_str = f"TEST 4 p{tnum}"
            for s in table.team_status:
                team_str += f" {s.usage}"
            if 4 in enable:
                nc.append(team_str)
            for cnum, c in enumerate(table.characters):
                # 5 for character status
                character_str = f"TEST 5 p{tnum}c{cnum}"
                for s in c.status:
                    character_str += f" {s.usage}"
                if 5 in enable:
                    nc.append(character_str)
                cdesc_str = f"TEST 10 p{tnum}c{cnum} |{c.desc}|"
                if c.is_alive and 10 in enable:
                    nc.append(cdesc_str)
                cele_str = f"TEST 12 p{tnum}c{cnum}"
                for e in c.element_application:
                    cele_str += f" {e.value}"
                if c.is_alive and 12 in enable:
                    nc.append(cele_str)
            # 6 for hands
            hands_str = f"TEST 6 p{tnum} {len(table.hands)}"
            if 6 in enable:
                nc.append(hands_str)
            # 7 for dice
            dice_str = f"TEST 7 p{tnum}"
            for c in table.dice.colors:
                dice_str += f" {c.value}"
            if 7 in enable:
                nc.append(dice_str)
            # 9 for summon element
            summon_element_str = f"TEST 9 p{tnum}"
            for summon in table.summons:
                summon_element_str += " " + summon.damage_elemental_type.value
            if 9 in enable:
                nc.append(summon_element_str)
        # 8 for character charge
        charge_str = "TEST 8"
        for i in range(2):
            for c in match.player_tables[i].characters:
                charge_str += " " + str(c.charge)
        if 8 in enable:
            nc.append(charge_str)
        # 11 for hand usage availability
        hand_usage_str = "TEST 11"
        for req in match.requests:
            if req.name == "UseCardRequest":
                hand_usage_str += " " + str(req.card_idx)
        if 11 in enable:
            nc.append(hand_usage_str)
        # filter tests
        while True:
            nc.append(agent.commands[0])
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR
    json_data["command_history"] = new_commands
    open(json_path, "w").write((json.dumps(json_data, indent=4)))


if __name__ == "__main__":
    template()
