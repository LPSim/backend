from .agent_base import AgentBase
from ..server.match import Match
from ..server.interaction import (
    Responses,
    SwitchCardResponse,
    ChooseCharacterResponse,
    RerollDiceResponse,
    DeclareRoundEndResponse,
)


class NothingAgent(AgentBase):
    """
    Agent that do nothing, only response essential requests.
    """

    def generate_response(self, match: Match) -> Responses | None:
        for req in match.requests:
            if req.player_idx == self.player_idx:
                if req.name == "SwitchCardRequest":
                    return SwitchCardResponse(request=req, card_idxs=[])
                elif req.name == "ChooseCharacterRequest":
                    return ChooseCharacterResponse(
                        request=req, character_idx=req.available_character_idxs[0]
                    )
                elif req.name == "RerollDiceRequest":
                    return RerollDiceResponse(request=req, reroll_dice_idxs=[])
                elif req.name == "DeclareRoundEndRequest":
                    return DeclareRoundEndResponse(request=req)
