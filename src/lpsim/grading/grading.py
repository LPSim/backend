import json
import os

from src.lpsim.server.consts import ObjectType


TEST_MATCH = os.path.dirname(os.path.abspath(__file__)) + "/match_1.json"


class Grading:
    def __init__(self, match: str):
        with open(match) as f:
            self.data = json.load(f)
        self.expected_turn = 4
        self.current_turn = 0
        self.character_element = []
        self.grading_rules = {}
        self.grade_match(self.data)

    def load_grading(self, obj_type, name, version):
        key = "%s+%s+%s" % (obj_type, name, version)
        if key in self.grading_rules.keys():
            return self.grading_rules[key]
        grading_file = os.path.dirname(os.path.abspath(__file__)) + "/grading_rules/%s/%s+%s" % (obj_type, name, version)
        with open(grading_file) as f:
            rule = json.load(f)
        self.grading_rules[key] = rule
        return rule

    def grade_by_rule(self, obj_type, name, version, usage):
        rule = self.load_grading(obj_type, name, version)
        a = rule[0]
        q = rule[1]
        n = usage
        if usage == 0:
            n = max(1, self.expected_turn - self.current_turn)
        return a * (1 - pow(q, n)) / (1 - q)

    def grade_match(self, match):
        self.current_turn = match["round_number"]
        return self.grade_player(match["player_tables"][0]) - self.grade_player(match["player_tables"][1])

    def grade_player(self, player):
        grade = 0
        for character in player["characters"]:
            grade += self.grade_character(character)
        for status in player["team_status"]:
            grade += self.grade_team_status(status)
        grade += self.grade_dice(player["dice"])
        grade += self.grade_hands(player["hands"])
        for summon in player["summons"]:
            grade += self.grade_summon(summon)
        for support in player["supports"]:
            grade += self.grade_support(support)
        return grade

    def grade_character(self, character):
        grade = 0
        if character["name"] == "Barbara":
            self.expected_turn += 5
        if character["name"] == "Dehya":
            self.expected_turn += 2
        # grading hp
        grade += character["hp"] * 10
        # grading attaches
        grade += self.grade_attaches(character["attaches"])
        # register elements
        self.character_element.append(character["element"])
        return grade

    def grade_attaches(self, attaches):
        grade = 0
        for attach in attaches:
            print(attach)
            if attach["type"] == "character_status":
                grade += self.grade_character_status(attach)
            else:
                grade += self.grade_character_status(attach)
        return 0

    def grade_dice(self, dice):
        effect_dice = 0
        for dice in dice["colors"]:
            if dice == "OMNI" or dice in self.character_element:
                effect_dice += 1
        return effect_dice * 5 + len(dice)

    def grade_hands(self, hands):
        return len(hands) * 5

    def grade_summon(self, summon):
        return self.grade_by_rule("summon", summon["name"], summon["version"], summon["usage"])

    def grade_support(self, support):
        return self.grade_by_rule("support", support["name"], support["version"], support["usage"])

    def grade_character_status(self, status):
        return self.grade_by_rule("character_status", status["name"], status["version"], status["usage"])

    def grade_team_status(self, status):
        return self.grade_by_rule("team_status", status["name"], status["version"], status["usage"])


if __name__ == "__main__":
    grading = Grading(TEST_MATCH)
