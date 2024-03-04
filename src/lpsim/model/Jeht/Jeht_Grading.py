from src.lpsim.model.model import model


class JehtGrading():
    def __init__(self, match, player):
        from src.lpsim.model.model import model
        m = model()
        self.match = m.get_match(match)
        self.player = self.match["player_tables"][player]
        self.opponent = self.match["player_tables"][1-player]
        self.elements = set()
        self.get_elements()

    def get_elements(self):

        for character in self.player["characters"]:
            self.elements.add(character["element"])