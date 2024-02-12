from lpsim.server.match import Match, MatchState
from lpsim.server.deck import Deck
from lpsim.agents.interaction_agent import InteractionAgent
from tests.utils_for_test import (
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_sunyata_no_default():
    """
    When sunyata generate card, then success. No need to check or use the card,
    as we don't know the newest version of cards.
    """
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 2 0 1 2",
            "card 0 0",
            "TEST 2 p0 hand 5",
            "TEST 3 p0 team 1",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "end",
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
        character:AnemoMobMage
        character:CryoMob
        character:PyroMobMage
        Jeht*10
        Sunyata Flower*20
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 2:
                assert 5 == len(match.player_tables[0].hands)
            elif test_id == 3:
                assert 1 == len(match.player_tables[0].team_status)
                assert 1 == match.player_tables[0].team_status[0].usage
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_sunyata_no_default()
