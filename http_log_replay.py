import sys
from lpsim.tools import interact_match_with_agents, read_log
from lpsim.network import HTTPServer
from lpsim.server.match import MatchConfig
import logging


logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    log_path = "logs.json"
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    log_str = open(log_path).read()
    agents, match = read_log(log_str, use_16_omni=None)
    # for i in range(2):
    #     characters = match.player_tables[i].player_deck_information.characters  # noqa: E501
    #     for c in characters:
    #         c.hp = c.max_hp = 30
    match.config.history_level = 10
    try:
        interact_match_with_agents(agents[0], agents[1], match)
    except Exception:
        print("*************************************************************")
        print("!!!!! ERROR: play log FAILED, play to last success log. !!!!!")
        print("*************************************************************")
    server = HTTPServer(
        decks=["", ""],
        match_config=MatchConfig(
            check_deck_restriction=False,
            card_number=None,
            max_same_card_number=None,
            character_number=None,
            max_round_number=999,
            random_first_player=False,
            history_level=10,
        ),
    )
    server.match = match

    server.run()
