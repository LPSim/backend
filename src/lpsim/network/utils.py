from typing import Any, List
from ..server.event_handler import OmnipotentGuideEventHandler
from ..server.match import Match, MatchConfig
from ..server.deck import Deck


def get_new_match(
    decks: List[Deck],
    seed: Any = None, 
    rich_mode: bool = False,
    match_config: MatchConfig | None = None,
    history_level: int = 10,
    make_skill_prediction: bool = True,
    auto_step: bool = True,
):
    """
    Generate new match with given conditions.

    Args:
        decks: The decks of players. If its length is zero, will not set decks
            or start the match.
        seed: The random seed. It should follow the format of numpy.random.
        rich_mode: If True, use rich mode, at round start, players is given
            16 omni dice. Mainly used in code testing.
        match_config: The config of the match. If None, use default config.
            Mainly used to set special rules, accept illegal decks, use
            recreate mode, etc.
        history_level: The level of history. Default is 10, to record important
            actions. Will have no effect when match_config is not None.
        make_skill_prediction: If True, make skill prediction. Will have no
            effect when match_config is not None.
        auto_step: If True, auto step the match once.
    Returns:
        The generated match. If generate failed or error occured, raise error.
    """
    if seed:
        match: Match = Match(random_state = seed)
    else:
        match: Match = Match()

    if match_config:
        match.config = match_config
    else:
        match.config.history_level = history_level
        match.config.make_skill_prediction = make_skill_prediction

    if rich_mode:
        match.config.initial_dice_number = 16
        match.event_handlers.append(OmnipotentGuideEventHandler())

    if len(decks) > 0:
        match.set_deck(decks)
        start_result = match.start()
        if not start_result:
            raise RuntimeError('Match start failed.')

    if auto_step:
        match._save_history()
        match.step()

    return match
