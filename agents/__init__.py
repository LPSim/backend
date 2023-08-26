from .interaction_agent import InteractionAgent
from .nothing_agent import NothingAgent
from .random_agent import RandomAgent


Agents = InteractionAgent | NothingAgent | RandomAgent
