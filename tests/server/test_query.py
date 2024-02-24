import pytest

from lpsim.server.character.character_base import SkillBase
from lpsim.server.consts import SkillType
from lpsim.server.deck import Deck
from lpsim.server.match import Match, MatchState
from lpsim.agents.interaction_agent import InteractionAgent
from tests.utils_for_test import get_random_state, make_respond, set_16_omni


def test_query_satisfy():
    cmd_records = [
        [
            "sw_card 1 2 3 4 0",
            "choose 1",
            "card 1 0 15",
            "sw_char 2 14 13",
            "end",
            "card 5 0",
            "card 2 3",
            "sw_char 3 15",
            "sw_char 2 14",
            "sw_char 3 13",
            "skill 1 12 11 10",
            "card 4 3",
            "card 0 3 10 9",
            "sw_char 1 9",
            "sw_char 3 8",
            "card 1 0 7 6 5",
            "skill 1 4 3 2",
            "skill 0 2 1 0",
            "end",
            "sw_char 4 15",
            "skill 1 14 13 12",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "sw_char 1 7",
            "sw_char 0 6",
            "end",
            "sw_char 4 15",
            "card 3 0 14 13 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "sw_char 0 7",
            "skill 1 6",
            "skill 1 5",
            "sw_char 4 4",
        ],
        [
            "sw_card 0 1 2 3 4",
            "choose 2",
            "card 0 0 15",
            "sw_char 4 13 12",
            "skill 0 11 10 9",
            "end",
            "sw_char 1 15",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "card 3 1 5",
            "sw_char 3 4",
            "sw_char 0 3",
            "skill 1 2",
            "end",
            "sw_char 1 15",
            "card 4 0 14 13 12",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "sw_char 1 7",
            "skill 0 6 5 4",
            "skill 0 3 4 2",
            "skill 0 1 2 0",
            "card 6 0",
            "end",
            "skill 0 15 14 13",
            "card 3 2",
            "sw_char 2 13",
            "card 2 0 12 11 10",
            "sw_char 4 9",
            "skill 1 8 7 6",
            "skill 0 5 4",
            "skill 0 3 2",
            "card 0 0 1",
            "end",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        "default_version:4.3\ncharacter:Yoimiya@3.8\ncharacter:Keqing@3.3\ncharacter:Dehya@4.1\ncharacter:Shenhe@4.2\ncharacter:Barbara@3.3\nLost Prayer to the Sacred Winds@4.3\nLost Prayer to the Sacred Winds@4.3\nTulaytullah's Remembrance@4.3\nTulaytullah's Remembrance@4.3\nBeacon of the Reed Sea@4.3\nBeacon of the Reed Sea@4.3\nPrimordial Jade Winged-Spear@4.3\nPrimordial Jade Winged-Spear@4.3\nLight of Foliar Incision@4.3\nLight of Foliar Incision@4.3\nFlowing Rings@4.3\nFlowing Rings@4.3\nEchoes of an Offering@4.3\nEchoes of an Offering@4.3\nHeart of Khvarena's Brilliance@4.3\nHeart of Khvarena's Brilliance@4.3\nVourukasha's Glow@4.3\nVourukasha's Glow@4.3\nThe Boar Princess@4.3\nThe Boar Princess@4.3\nFalls and Fortune@4.3\nFalls and Fortune@4.3\n"  # noqa: E501
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.random_first_player = False
    match.config.initial_hand_size = 5
    match.config.max_hand_size = 99
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR

    # test query_one
    p0c0 = match.player_tables[0].characters[0]
    p1c1 = match.player_tables[1].characters[1]
    p0c4 = match.player_tables[0].characters[4]
    p0 = match.player_tables[0].team_status[0]
    with pytest.raises(ValueError):
        p0c0.query_one(match, "both character")
    with pytest.raises(ValueError):
        p0c0.query_one(match, "our hand 'name=Vourukasha's Glow'")
    with pytest.raises(ValueError):
        p0c0.query_one(match, "both character name=Keqing")
    res = p0c0.query_one(match, "both character weapon 'name=Light of Foliar Incision'")
    assert res is not None and res.name == "Light of Foliar Incision"
    res = p0c0.query_one(match, "both character status 'usage=1'")
    assert res is not None and res.name == "Electro Elemental Infusion"
    with pytest.raises(ValueError):
        res = p0c0.query_one(match, "both character status 'usage=2'")
    with pytest.raises(ValueError):
        res = p0c0.query_one(match, "both active skill 'skill_type=elemental_burst'")
    res = p0c0.query_one(
        match, r"""both active weapon "name=Tulaytullah's Remembrance" """
    )
    assert res is not None and res.name == "Tulaytullah's Remembrance"
    sres: SkillBase = p0c0.query_one(
        match, "our active skill 'skill_type=elemental_burst'"
    )  # type: ignore
    assert (
        sres is not None
        and sres.position.player_idx == 0
        and sres.position.character_idx == 4
        and sres.skill_type == SkillType.ELEMENTAL_BURST
        and sres.name == "Shining Miracle"
    )
    sres = p0c0.query_one(match, "opponent active skill 'skill_type=elemental_burst'")  # type: ignore  # noqa: E501
    assert (
        sres is not None
        and sres.position.player_idx == 1
        and sres.position.character_idx == 4
        and sres.skill_type == SkillType.ELEMENTAL_BURST
        and sres.name == "Shining Miracle"
    )
    res = p0c0.query_one(match, "self status")  # type: ignore
    assert (
        res is not None
        and res.position.player_idx == 0
        and res.position.character_idx == 0
        and res.name == "Niwabi Enshou"
    )
    with pytest.raises(ValueError):
        res = p0c0.query_one(match, "opponent character status")
    res = p0c0.query_one(match, "opponent team_status")
    assert res is None
    res = p0c0.query_one(match, "our team_status")
    assert res is not None and res.name == "Icy Quill"
    with pytest.raises(AssertionError):
        p0c0.query_one(match, "self team_status")
    with pytest.raises(AssertionError):
        p0c0.query_one(match, "both weapon")
    with pytest.raises(AssertionError):
        p0c0.query_one(match, "our weapon")
    res = p0c0.query_one(
        match, "our team_status and opponent team_status and our support"
    )
    assert res is not None and res.name == "Icy Quill"
    with pytest.raises(ValueError):
        p0c0.query_one(match, "our character status and opponent character status")
    res = p0c0.query_one(match, "our character weapon", allow_multiple=True)
    assert res is not None and res.name in [
        "Lost Prayer to the Sacred Winds",
        "Primordial Jade Winged-Spear",
    ]
    with pytest.raises(ValueError):
        p0c0.query_one(match, "character")
    with pytest.raises(ValueError):
        p0c0.query_one(match, "both both both character")
    res = p0c0.query_one(match, "our next status")
    assert res is not None and res.name == "Niwabi Enshou"
    res = p0c0.query_one(match, "opponent prev")
    assert res is not None and res.name == "Shenhe"
    res = p1c1.query_one(match, "our character hp=2")
    assert res is not None and res.name == "Yoimiya"
    res = p1c1.query_one(match, "opponent character status usage=2")
    assert res is not None and res.name == "Niwabi Enshou"

    # test query
    res = p0c0.query(match, "both character")
    assert len(res) == 10
    res = p0c0.query(match, "both character weapon=None")
    assert len(res) == 6
    res = p0c0.query(match, "our character charge=0")
    assert len(res) == 2
    res = p0c0.query(match, "opponent character charge=2")
    assert len(res) == 0
    res = p0c0.query(match, "both next")
    assert len(res) == 2
    for r in res:
        assert r.name == "Yoimiya"
        assert r.position.character_idx == 0
    res = p0c0.query(match, "our summon usage=1")
    assert len(res) == 0
    res = p0c0.query(match, "our summon usage=2")
    assert len(res) == 1 and res[0].name == "Melody Loop"
    res = p0c0.query(match, "both summon usage=2")
    assert len(res) == 2
    for r in res:
        assert r.name == "Melody Loop"
    res = p0c0.query(match, "our hand 'name=Primordial Jade Winged-Spear'")
    assert len(res) == 1 and res[0].name == "Primordial Jade Winged-Spear"
    res = p0c0.query(match, "both hand 'name=Primordial Jade Winged-Spear'")
    assert len(res) == 3
    for r in res:
        assert r.name == "Primordial Jade Winged-Spear"
    res = p0c0.query(match, "both character artifact")
    assert len(res) == 4
    res = p0c0.query(match, "our deck")
    assert len(res) == 9
    res = p1c1.query(match, "our hand 'name=Lost Prayer to the Sacred Winds'")
    assert len(res) == 2
    res = p1c1.query(match, "our hand 'name=Lost Prayer to the Sacred Winds'")
    with pytest.raises(AssertionError):
        p0.query(match, "self")

    # satisfy
    p0c0 = p0c0.position
    p1c1 = p1c1.position
    p0c4 = p0c4.position
    p0 = p0.position
    with pytest.raises(AssertionError):
        p0c0.satisfy("source active=true")
    with pytest.raises(AssertionError):
        p0c0.satisfy("target active=true")
    with pytest.raises(AssertionError):
        p0c0.satisfy("target pidx=1")
    with pytest.raises(AssertionError):
        p0c0.satisfy("source pidx=0 and target pidx=1")
    with pytest.raises(AssertionError):
        p0c0.satisfy("source pidx=0 active=false")
    assert not p0c0.satisfy("source pidx=1")
    assert not p0c0.satisfy("source active=true", match=match)
    assert p0c4.satisfy("source active=true", match=match)
    assert not p0c4.satisfy("source active=true pidx=1", match=match)
    assert p0c4.satisfy("source active=true pidx=0 cidx=4", match=match)
    assert p1c1.satisfy("source pidx=1 cidx=1")
    assert p0c4.satisfy("source pidx=0 cidx=4 and target pidx=1 cidx=1", target=p1c1)
    assert not p0c4.satisfy(
        "source pidx=0 cidx=4 and target pidx=1 cidx=2", target=p1c1
    )
    assert not p0c4.satisfy(
        "source pidx=0 cidx=2 and target pidx=1 cidx=1", target=p1c1
    )
    with pytest.raises(AssertionError):
        p0c0.satisfy("both pidx=same")
    with pytest.raises(ValueError):
        p0c0.satisfy("source active=1", match=match)
    with pytest.raises(ValueError):
        p0c0.satisfy("source sss=1", match=match)
    with pytest.raises(ValueError):
        p0c0.satisfy("source hahaha", match=match)
    with pytest.raises(ValueError):
        p0c0.satisfy("active=1", match=match)
    with pytest.raises(ValueError):
        p0.satisfy("source active=true", match=match)
    assert p1c1.satisfy(f"source id={p1c1.id}")
    assert not p1c1.satisfy(f"source id={p0c4.id}")
    assert p1c1.satisfy("source area=CHARACTER")
    assert p1c1.satisfy("source area=character")
    assert not p1c1.satisfy("source area=team_status")
    assert p0.satisfy("source area=team_status")
    # satisfy both
    with pytest.raises(ValueError):
        assert p0c0.satisfy("both pidx=0", match=match, target=p1c1)
    with pytest.raises(ValueError):
        assert p0c0.satisfy("both id=1", match=match, target=p1c1)
    with pytest.raises(ValueError):
        assert p0c0.satisfy("both id", match=match, target=p1c1)
    with pytest.raises(ValueError):
        assert p0c0.satisfy("both di=same", match=match, target=p1c1)
    assert not p0c0.satisfy("both id=same", match=match, target=p1c1)
    assert p0c0.satisfy("both pidx=diff", match=match, target=p1c1)
    assert p0c0.satisfy("both pidx=same cidx=diff", match=match, target=p0)
    assert not p0c0.satisfy("both pidx=same cidx=same", match=match, target=p0c4)
    assert p0c0.satisfy(
        "both pidx=same cidx=diff and source pidx=0 and target area=character",
        match=match,
        target=p0c4,
    )
    assert not p0c0.satisfy(
        "both pidx=same cidx=diff and source pidx=1 and target area=character",
        match=match,
        target=p0c4,
    )
    assert not p0c0.satisfy(
        "both pidx=same cidx=diff and source pidx=0 and target area=character_status",
        match=match,
        target=p0c4,
    )
    assert not p0c0.satisfy("both pidx=diff cidx=diff", match=match, target=p0)
    assert p0c0.satisfy("both pidx=same cidx=diff id=diff", match=match, target=p0)
    assert not p0c0.satisfy("both pidx=same cidx=diff id=same", match=match, target=p0)
    assert p0c0.satisfy(
        "both pidx=same cidx=diff id=diff area=diff", match=match, target=p0
    )
    assert p0c0.not_satisfy(
        "both pidx=same cidx=diff id=diff area=same", match=match, target=p0
    )
    assert p0c0.not_satisfy(
        "both pidx=same cidx=diff id=diff area=same", match=match, target=p0
    )
    assert p0c0.satisfy(
        "both pidx=same cidx=diff id=diff area=same", match=match, target=p0c4
    )


if __name__ == "__main__":
    test_query_satisfy()
