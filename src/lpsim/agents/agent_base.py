"""
Base class of all agents.
"""
from ..server.interaction import Responses
from ..server.match import Match
from ..utils import BaseModel


class AgentBase(BaseModel):
    """
    Base class of all agents.
    """
    player_idx: int

    def generate_response(self, match: Match) -> Responses | None:
        """
        generate response based on the match. Return None if no response is
        generated.
        """
        raise NotImplementedError()
