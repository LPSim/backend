from .agent_base import AgentBase
from server.match import Match
from server.interaction import (
    Responses,
    SwitchCardResponse,
    ChooseCharactorResponse,
    RerollDiceResponse,
    DeclareRoundEndResponse
)


class NothingAgent(AgentBase):
    """
    Agent that do nothing.
    """
    def generate_response(self, match: Match) -> Responses | None:
        for req in match.requests:
            if req.player_id == self.player_id:
                if req.name == 'SwitchCardRequest':
                    return SwitchCardResponse(
                        request = req, card_ids = []
                    )
                elif req.name == 'ChooseCharactorRequest':
                    return ChooseCharactorResponse(
                        request = req, 
                        charactor_id = req.available_charactor_ids[0]
                    )
                elif req.name == 'RerollDiceRequest':
                    return RerollDiceResponse(
                        request = req, reroll_dice_ids = []
                    )
                elif req.name == 'DeclareRoundEndRequest':
                    return DeclareRoundEndResponse(
                        request = req
                    )
