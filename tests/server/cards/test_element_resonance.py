from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_woven_element():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 dendro pyro anemo hydro dendro "
            "cryo dendro electro dendro pyro",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "TEST 2 color match",
            "end"
        ]
    ]
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = cmd_records[0],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = cmd_records[1],
        only_use_command = True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state = get_random_state())
    # deck information
    deck = Deck.from_str(
        '''
        charactor:Nahida*3
        Elemental Resonance: Woven Flames*4
        Elemental Resonance: Woven Ice*4
        Elemental Resonance: Woven Stone*4
        Elemental Resonance: Woven Thunder*4
        Elemental Resonance: Woven Waters*4
        Elemental Resonance: Woven Weeds*4
        Elemental Resonance: Woven Winds*4
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
    match.start()
    match.step()

    record = []
    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                colors = [x.upper() for x in cmd.split(' ')[2:]]
                colors = [colors[:5], colors[5:]]
                for i in range(2):
                    for j in range(5):
                        assert match.player_tables[
                            i].hands[j].element == colors[i][j]  # type: ignore
                record = colors
            elif test_id == 2:
                for table, rec in zip(match.player_tables, record):
                    m = {}
                    for r in rec:
                        m[r] = m.get(r, 0) + 1
                    for color in table.dice.colors:
                        if color != 'OMNI':

                            m[color.name] -= 1
                    for v in m.values():
                        assert v == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_woven_element()
