import json

TEST_MATCH = "../model/match_1.json"


class Grading:
    def __init__(self, match: str):
        with open(match) as f:
            self.data = json.load(f)
        print(self.data["player_tables"])

    def grade_match(self, match):
        pass

    def grade_player(self, player):
        pass

    def grade_character(self, character):
        pass

    def grade_attach(self, attach):
        pass

    def grade_card(self, card):
        pass

    def grade_character_status(self, status):
        pass

    def grade_deck(self, deck):
        pass

    def grade_dice(self, dice):
        pass

    def grade_hands(self, hands):
        pass

    def grade_summon(self, summon):
        pass

    def grade_support(self, support):
        pass

    def grade_team_status(self, status):
        pass


if __name__ == "__main__":
    grading = Grading(TEST_MATCH)
