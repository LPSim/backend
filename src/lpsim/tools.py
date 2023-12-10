"""
Tools that based on other modules.
"""
import json
from typing import List, Tuple

from .server.event_handler import OmnipotentGuideEventHandler_3_3

from .server.deck import Deck
from .server.match import Match, MatchConfig, MatchState
from .agents.interaction_agent import InteractionAgent


def read_log(
    log_str: str, use_16_omni: bool | None = None
) -> Tuple[List[InteractionAgent], Match]:
    """
    Read log and return agents and a match.

    Args:
        log_str (str): log string with JSON format. It must contain 
            `start_deck`, `match_random_state` and `command_history`, and 
            optionally `match_config`.
        use_16_omni (bool | None, optional): If True, use OmnipotentGuide.
            If False, not use it. If None, determined by dice number from
            match_config, if config exists and is 16 then True, otherwise 
            False.
    """
    data = json.loads(log_str)
    if 'version' not in data:
        data['version'] = '1.0'
    if data['version'] == '1.0':
        decks = []
        for d in data['start_deck']:
            if isinstance(d, str):
                decks.append(Deck.from_str(d))
            else:
                decks.append(Deck(**d))
        match = Match(random_state = data['match_random_state'])
        if 'match_config' in data:
            match.config = MatchConfig(**data['match_config'])
        if use_16_omni is None:
            if (
                'match_config' in data
                and data['match_config']['initial_dice_number'] == 16
            ):
                use_16_omni = True
            else:
                use_16_omni = False
        if use_16_omni:
            match.event_handlers.append(OmnipotentGuideEventHandler_3_3())
        match.set_deck(decks)
        commands = data['command_history']
        agents: List[InteractionAgent] = []
        for cnum, command in enumerate(commands):
            agent = InteractionAgent(
                player_idx = cnum, 
                commands = command,
                only_use_command = True
            )
            agents.append(agent)
        return agents, match
    else:
        raise ValueError(f'Unknown log version: {data["version"]}')


def interact_match_with_agents(
    agent_0: InteractionAgent, agent_1: InteractionAgent, match: Match
) -> None:
    """
    Interact match with agents.
    """
    if match.state == MatchState.WAITING:
        assert match.start()[0]
    match.step()
    while len(agent_1.commands) > 0 or len(agent_0.commands) > 0:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # respond
        resp = agent.generate_response(match)
        assert resp is not None
        match.respond(resp)
        match.step()
