import os
from tests.utils_for_test import do_log_tests


def test_balance():
    json_fname = "balance_thuncer_vourukashas_stove.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path, hp_modify=10)


def test_cryo_hypostasis():
    json_fname = "cryo_hypostasis.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def millennial_999_test(match, cmd):
    """
    p0c0 millennial is talent status 0
    """
    status = match.player_tables[0].characters[0].status[0]
    assert status.desc == "talent"


def test_millennial_pearl_seahorse():
    json_fname = "millennial_pearl_seahorse.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path, other_tests={999: millennial_999_test})


def test_millennial_pearl_seahorse_2():
    json_fname = "millennial_pearl_seahorse2.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_thoma():
    json_fname = "thoma.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_sayu():
    json_fname = "sayu.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_sapwood_machine_veteran():
    json_fname = "sapwood_machine_veteran.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_machine_2():
    json_fname = "machine_2.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_veteran_2():
    json_fname = "veteran_2.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_silver():
    json_fname = "silver.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_jeht_sunyata():
    json_fname = "jeht_sunyata.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


if __name__ == "__main__":
    # test_balance()
    test_cryo_hypostasis()
    # test_millennial_pearl_seahorse()
    # test_millennial_pearl_seahorse_2()
    test_thoma()
    test_sayu()
    # test_sapwood_machine_veteran()
    # test_machine_2()
    # test_veteran_2()
    # test_silver()
