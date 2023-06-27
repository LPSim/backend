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
    from server.interaction import SwitchCardResponse, ChooseCharactorResponse
    main.match.respond(SwitchCardResponse(
        request = main.match.requests[0], card_ids = [3, 1, 2]))
    main.match.respond(SwitchCardResponse(
        request = main.match.requests[0], card_ids = [3, 1, 2]))
    main.match.step()  # choose charactor
    main.match.respond(ChooseCharactorResponse(
        request = main.match.requests[0], charactor_id = 0
    ))
    main.match.respond(ChooseCharactorResponse(
        request = main.match.requests[0], charactor_id = 1
    ))
    main.match.step()
    print(main.json())
