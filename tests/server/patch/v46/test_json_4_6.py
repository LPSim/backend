import os
from tests.utils_for_test import do_log_tests, get_pidx_cidx


def test_beidou_candace_v46():
    json_fname = "beidou_candace.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_jeht_seed_yayoi_v46():
    json_fname = "jeht_seed_yayoi.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_macaron_seirai_gongyi_v46():
    json_fname = "macaron_seirai_gongyi.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def check_counter(match, cmd):
    pidx, cidx = get_pidx_cidx(cmd)
    c = match.player_tables[pidx].characters[cidx]
    assert c.is_alive
    eq_counter_str = ""
    assert c.weapon is None
    eq_counter_str += "N"
    if c.artifact is None:
        eq_counter_str += "N"
    else:
        eq_counter_str += str(
            c.artifact.counter  # type: ignore
            if hasattr(c.artifact, "counter")
            else "-"
        )
    assert c.talent is None
    eq_counter_str += "N"


def test_amethyst_crown_v46():
    json_fname = "amethyst_crown.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path, other_tests={114: check_counter})


def test_yayoi_nanatsuki_multiple_v46():
    json_fname = "yayoi_nanatsuki.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_two_abyss_v46():
    json_fname = "two_abyss.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_abyss_fire_talent_v46():
    json_fname = "abyss_fire_talent.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_kuki_shinobu_v46():
    json_fname = "kuki_shinobu.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_crab_v46():
    json_fname = "crab.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_crab_2_v46():
    json_fname = "crab_2.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_crab_3_v46():
    json_fname = "crab_3.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_faruzan_v46():
    json_fname = "faruzan.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_faruzan_2_v46():
    json_fname = "faruzan_2.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_faruzan_3_v46():
    json_fname = "faruzan_3.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


if __name__ == "__main__":
    # test_beidou_candace_v46()
    # test_jeht_seed_yayoi_v46()
    # test_macaron_seirai_gongyi_v46()
    # test_amethyst_crown_v46()
    # test_yayoi_nanatsuki_multiple_v46()
    # test_two_abyss_v46()
    # test_abyss_fire_talent_v46()
    # test_kuki_shinobu_v46()
    # test_crab_v46()
    # test_crab_2_v46()
    # test_crab_3_v46()
    # test_faruzan_v46()
    # test_faruzan_2_v46()
    test_faruzan_3_v46()
