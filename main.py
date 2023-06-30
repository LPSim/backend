import logging
from server.match import Match
from utils import BaseModel
from server.deck import Deck


class Main(BaseModel):
    """
    """

    version: str = '1.0.0'
    name: str = 'GITCG'
    match: Match = Match()


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    main = Main()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'CharactorBase',
                'element': 'DENDRO',
            }
        ] * 3,
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    main.match.set_deck([deck, deck])
    main.match.match_config.max_same_card_number = 30
    assert main.match.start()
    main.match.step()  # switch card
    from server.interaction import (
        SwitchCardResponse, ChooseCharactorResponse, RerollDiceResponse
    )
    from server.consts import DiceColor
    # switch 3 cards
    main.match.respond(SwitchCardResponse(
        request = main.match.requests[0], card_ids = [3, 1, 2]))
    main.match.respond(SwitchCardResponse(
        request = main.match.requests[0], card_ids = [3, 1, 2]))
    main.match.step()
    # choose charactor
    main.match.respond(ChooseCharactorResponse(
        request = main.match.requests[0], charactor_id = 0
    ))
    main.match.respond(ChooseCharactorResponse(
        request = main.match.requests[0], charactor_id = 1
    ))
    main.match.step()
    # reroll dice not dendro or omni
    main.match.respond(RerollDiceResponse(
        request = main.match.requests[0], 
        reroll_dice_ids = [
            x for x in range(8) 
            if main.match.requests[0].dice_colors[x] not in (
                DiceColor.DENDRO, DiceColor.OMNI
            )
        ]
    ))
    main.match.respond(RerollDiceResponse(
        request = main.match.requests[0],
        reroll_dice_ids = [
            x for x in range(8) 
            if main.match.requests[0].dice_colors[x] not in (
                DiceColor.DENDRO, DiceColor.OMNI
            )
        ]
    ))
    main.match.step()
    print(main.json())
