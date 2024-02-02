import os

from lpsim.server.deck import Deck

from lpsim.server.match import Match
from lpsim.agents.interaction_agent import InteractionAgent
from lpsim import MatchState
from tests.utils_for_test import (
    check_hp,
    check_usage,
    get_pidx_cidx,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    read_from_log_json,
    set_16_omni,
)


def test_azhdaha():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), "jsons", "test_azhdaha.json")
    )
    # modify hp
    # for i in range(2):
    #     characters = match.player_tables[i].player_deck_information.characters  # noqa: E501
    #     for c in characters:
    #         c.hp = c.max_hp = 30
    # add omnipotent guide
    # set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        # do tests
        while True:
            cmd = agent.commands[0].strip().split(" ")
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
                pidx = int(cmd[2][1])
                colors = {}
                for c in cmd[3:]:
                    c, n = c.strip().split("*")
                    colors[c] = int(n)
                for c in match.player_tables[pidx].dice.colors:
                    c = c.value.lower()
                    assert c in colors
                    colors[c] -= 1
                    if colors[c] == 0:
                        del colors[c]
            elif test_id == 3:
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].characters[cidx].status
                check_usage(status, cmd[4:])
            elif test_id == 4:
                pidx, cidx = get_pidx_cidx(cmd)
                desc = cmd[-1]
                assert match.player_tables[pidx].characters[cidx].desc.lower() == desc
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_azhdaha_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "sw_char 2 15",
            "TEST 4 p0c2 desc empty",
            "skill 1 14 13 12",
            "TEST 4 p0c2 desc pyro",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "TEST 4 p0c1 desc cryo",
            "end",
        ],
        [
            "sw_card",
            "choose 4",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 3 9",
            "skill 1 8 7 6",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        default_version:4.3
        character:Azhdaha*3
        character:Kaeya
        character:Klee
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        # do tests
        while True:
            cmd = agent.commands[0].strip().split(" ")
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 4:
                pidx, cidx = get_pidx_cidx(cmd)
                desc = cmd[-1]
                if desc == "empty":
                    desc = ""
                assert match.player_tables[pidx].characters[cidx].desc.lower() == desc
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_azhdaha()
    test_azhdaha_2()
