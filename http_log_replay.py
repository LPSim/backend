import sys
from src.lpsim.tools import interact_match_with_agents, read_log
from src.lpsim.network import HTTPServer
from src.lpsim.server.match import MatchConfig
import logging


logging.basicConfig(level = logging.INFO)


if __name__ == '__main__':
    log_path = 'logs.json'
    log_path = r'.\src\lpsim\server\patch\v43\tests\test_alhaitham'
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    log_str = open(log_path).read()
    agents, match = read_log(log_str)
    match.config.history_level = 10
    interact_match_with_agents(agents[0], agents[1], match)
    server = HTTPServer(
        decks = ['', ''],
        match_config = MatchConfig(
            check_deck_restriction = False,
            card_number = None,
            max_same_card_number = None,
            charactor_number = None,
            max_round_number = 999,
            random_first_player = False,
            history_level = 10,
        )
    )
    server.match = match

    server.run()
