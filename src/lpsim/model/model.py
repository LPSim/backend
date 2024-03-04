import json
import os

from src.lpsim.server import *
from src.lpsim.server.consts import ObjectType
from src.lpsim.server.dice import Dice
from src.lpsim.server.match import Match
from src.lpsim.server.player_table import PlayerTable
from src.lpsim.utils import *

PROTOTYPE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"


class model:
    def get_prototype(self, obj_str):
        with open(PROTOTYPE_PATH + obj_str + ".json") as f:
            data = json.load(f)
        return data

    def match_to_json(self, match, name):
        match_data = self.get_match(match)
        with open(PROTOTYPE_PATH + name + ".json", 'w') as f:
            json.dump(match_data, f, indent=4)

    def json_to_match(self, name):
        with open(PROTOTYPE_PATH + name + ".json", 'r') as f:
            data = json.load(f)
        return self.set_match(data)

    def get_match(self, match):
        match_model = self.get_prototype("match")
        match_model["name"] = match.name
        match_model["version"] = match.version
        match_model["round_number"] = match.round_number
        match_model["current_player"] = match.current_player
        match_model["player_tables"] = [self.get_player(x) for x in match.player_tables]
        return match_model

    def set_match(self, match_model):
        match = Match()
        match.name = match_model["name"]
        match.version = match_model["version"]
        match.round_number = match_model["round_number"]
        match.current_player = match_model["current_player"]
        match.player_tables = [self.set_player(x) for x in match_model["player_tables"]]
        return match

    def get_player(self, player):
        player_model = self.get_prototype("player")
        player_model["name"] = player.name
        player_model["version"] = player.version
        player_model["player_idx"] = player.player_idx
        player_model["active_character_idx"] = player.active_character_idx
        player_model["has_round_ended"] = player.has_round_ended
        player_model["arcane_legend"] = player.arcane_legend
        player_model["plunge_satisfied"] = player.plunge_satisfied
        player_model["dice"] = self.get_dice(player.dice)
        player_model["characters"] = [self.get_character(x) for x in player.characters]
        player_model["team_status"] = [self.get_team_status(x) for x in player.team_status]
        player_model["summons"] = [self.get_summon(x) for x in player.summons]
        player_model["supports"] = [self.get_support(x) for x in player.supports]
        player_model["hands"] = self.get_hands(player.hands)
        player_model["table_deck"] = self.get_deck(player.table_deck)
        return player_model

    def set_player(self, player_model):
        player = PlayerTable(
            version=player_model["version"],
            player_idx=player_model["player_idx"],
        )
        player.dice = self.set_dice(player_model["dice"])
        player.characters = [self.set_character(x) for x in player_model["characters"]]
        player.team_status = [self.set_character_status(x) for x in player_model["team_status"]]
        player.summons = [self.set_character_status(x) for x in player_model["summons"]]
        player.supports = [self.set_character_status(x) for x in player_model["supports"]]
        player.hands = self.set_hands(player_model["hands"])
        player.table_deck = self.set_deck(player_model["table_deck"])
        return player

    def get_character(self, character):
        character_model = self.get_prototype("character")
        character_model["name"] = character.name
        character_model["version"] = character.version
        character_model["element"] = character.element
        character_model["hp"] = character.hp
        character_model["charge"] = character.charge
        character_model["attaches"] = [self.get_attach(x) for x in character.attaches]
        character_model["element_application"] = character.element_application
        character_model["is_alive"] = character.is_alive
        return character_model

    def set_character(self, character_model):
        args = {"name": character_model["name"], "version": character_model["version"]}
        character = get_instance(CharacterBase, args)
        character.attaches = [self.set_attach(x) for x in character_model["attaches"]]
        return character

    def get_attach(self, attach):
        if attach.type == ObjectType.CHARACTER_STATUS:
            attach_model = self.get_character_status(attach)
            attach_model["type"] = "character_status"
            return attach_model
        else:
            attach_model = self.get_card(attach)
            attach_model["type"] = "equipment"
            return attach_model

    def set_attach(self, attach_model):
        if attach_model["type"] == "character_status":
            return self.set_character_status(attach_model)
        elif attach_model["type"] == "equipment":
            return self.set_card(attach_model)

    def get_card(self, card):
        if card is None:
            return None
        card_model = self.get_prototype("card")
        card_model["name"] = card.name
        card_model["version"] = card.version
        return card_model

    def set_card(self, card_model):
        if card_model is None:
            return None
        return get_instance(CardBase, card_model)

    def get_character_status(self, status):
        character_status_model = self.get_prototype("character_status")
        character_status_model["name"] = status.name
        character_status_model["version"] = status.version
        character_status_model["usage"] = status.usage
        character_status_model["max_usage"] = status.max_usage
        return character_status_model

    def set_character_status(self, status_model):
        return get_instance(CharacterStatusBase, status_model)

    def get_deck(self, deck):
        return [self.get_card(x) for x in deck]

    def set_deck(self, deck_model):
        return [get_instance(CardBase, x) for x in deck_model]

    def get_dice(self, dice):
        dice_model = self.get_prototype("dice")
        dice_model["colors"] = dice.colors
        return dice_model

    def set_dice(self, dice_model):
        dice = Dice()
        dice.colors = dice_model["colors"]
        return dice

    def get_hands(self, hands):
        return [self.get_card(x) for x in hands]

    def set_hands(self, hands_model):
        return [get_instance(CardBase, x) for x in hands_model]

    def get_summon(self, summon):
        summon_model = self.get_prototype("summon")
        summon_model["name"] = summon.name
        summon_model["version"] = summon.version
        summon_model["usage"] = summon.usage
        summon_model["max_usage"] = summon.max_usage
        return summon_model

    def set_summon(self, summon_model):
        return get_instance(SummonBase, summon_model)

    def get_support(self, support):
        support_model = self.get_prototype("support")
        support_model["name"] = support.name
        support_model["version"] = support.version
        support_model["usage"] = support.usage
        return support_model

    def set_support(self, support_model):
        return get_instance(SupportBase, support_model)

    def get_team_status(self, status):
        team_status_model = self.get_prototype("team_status")
        team_status_model["name"] = status.name
        team_status_model["version"] = status.version
        team_status_model["usage"] = status.usage
        team_status_model["max_usage"] = status.max_usage
        return team_status_model

    def set_team_status(self, status_model):
        return get_instance(TeamStatusBase, status_model)


if __name__ == "__main__":
    from src.lpsim.server.deck import Deck
    from src.lpsim.agents import RandomAgent
    agent_0 = RandomAgent(player_idx=0)
    agent_1 = RandomAgent(player_idx=1)
    deck = Deck.from_str(
        '''
        default_version:4.1
        character:Rhodeia of Loch
        character:Kamisato Ayaka
        character:Yaoyao
        Traveler's Handy Sword*5
        Gambler's Earrings*5
        Kanten Senmyou Blessing*5
        Sweet Madame*5
        Abyssal Summons*5
        Fatui Conspiracy*5
        Timmie*5
        '''
    )
    match = Match()
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.history_level = 10
    match.config.check_deck_restriction = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
    match.config.card_number = None
    assert match.start()[0]
    match.step()

    while match.round_number < 3 \
            and not match.is_game_end():
        if match.need_respond(0):
            current_agent = agent_0
        elif match.need_respond(1):
            current_agent = agent_1
        else:
            raise RuntimeError("no agent need to respond")
        resp = current_agent.generate_response(match)
        assert resp is not None
        match.respond(resp)
        match.step()

    Model = model()
    Model.match_to_json(match, "match_1")
    match = Model.json_to_match("match_1")
    Model.match_to_json(match, "match_2")
    assert Model.get_prototype("match_1") == Model.get_prototype("match_2")
