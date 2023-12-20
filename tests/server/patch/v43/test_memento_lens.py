from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import get_random_state, make_respond, set_16_omni


def test_memento_lens():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "sw_char 2 15",
            "card 1 0 14",
            "card 1 1 13 12",
            "sw_char 0 11",
            "end",
            "card 2 2",
            "card 2 2 15 14",
            "end",
            "card 1 0 15 14",
            "card 3 0 13 12",
            "card 1 0 11 10 9",
            "card 0 0 8",
            "card 0 0",
            "end",
            "sw_char 1 15"
        ],
        [
            "sw_card",
            "choose 1",
            "card 0 1 15 14",
            "sw_char 2 13",
            "card 1 2 12 11",
            "end",
            "card 3 0 15 14 13",
            "card 1 0 12",
            "sw_char 1 11",
            "end",
            "card 3 0 15",
            "card 2 0",
            "card 2 0 14",
            "card 0 0 13",
            "end",
            "card 0 0",
            "card 1 0 15 14 13",
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
        charactor:Ningguang@3.3
        charactor:Kaeya@3.3
        charactor:Chongyun@3.3
        Sacrificial Fragments@3.3*5
        Instructor's Cap@3.3*5
        Chinju Forest@3.7*5
        Paimon@3.3*5
        Memento Lens@4.3*5
        Abyssal Summons@3.3*5
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
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
            raise AssertionError('No need respond.')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_memento_lens()
