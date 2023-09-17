from .interaction_agent import InteractionAgent
from .nothing_agent import NothingAgent
from .random_agent import RandomAgent
from .agent_base import AgentBase  # noqa: F401


Agents = InteractionAgent | NothingAgent | RandomAgent
