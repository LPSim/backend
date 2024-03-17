import os
from tests.utils_for_test import do_log_tests


def test_arcane_blast_v45():
    json_fname = "arcane_blast_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_lumenstone_enternalflow_v45():
    json_fname = "lumenstone_enternalflow_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_balance_v45():
    json_fname = "balance_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_meropide_golden_v45():
    json_fname = "meropide_golden_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_coverage_improve_v45():
    json_fname = "coverage_improve_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_neuvillette_v45():
    json_fname = "neuvillette_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_kirara_v45():
    json_fname = "kirara_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_charlotte_v45():
    json_fname = "charlotte_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_electro_cicin_mage_v45():
    json_fname = "electro_cicin_mage_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_electro_cicin_mage_2_v45():
    json_fname = "electro_cicin_mage_2_v45.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


if __name__ == "__main__":
    test_arcane_blast_v45()
    test_balance_v45()
    test_lumenstone_enternalflow_v45()
    test_meropide_golden_v45()
    test_coverage_improve_v45()
    test_neuvillette_v45()
    test_kirara_v45()
    test_charlotte_v45()
    test_electro_cicin_mage_v45()
