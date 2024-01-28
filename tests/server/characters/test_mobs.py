import pytest
from lpsim.server.deck import Deck


def test_create_mob():
    TEST_DECK = {
        "name": "Deck",
        "characters": [
            {
                "name": "PhysicalMob",
                "element": "ELECTRO",
            },
            {
                "name": "ElectroMobMage",
                "element": "ELECTRO",
            },
            {
                "name": "ElectroMob",
                "element": "ELECTRO",
            },
            {
                "name": "DendroMob",
            },
            {
                "name": "DendroMobMage",
            },
        ],
        "cards": [
            {
                "name": "Strategize",
            }
        ]
        * 30,
    }
    Deck(**TEST_DECK)
    TEST_DECK["characters"][1]["element"] = "DENDRO"
    with pytest.raises(ValueError):
        Deck(**TEST_DECK)
    TEST_DECK["characters"][1]["element"] = "ELECTRO"
    TEST_DECK["characters"][2]["element"] = "DENDRO"
    with pytest.raises(ValueError):
        Deck(**TEST_DECK)
    TEST_DECK["characters"][2]["element"] = "ELECTRO"
