import os
from tests.utils_for_test import do_log_tests


def test_issue_106():
    json_fname = "test_issue_106.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


def test_issue_82():
    json_fname = "test_issue_82.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path)


if __name__ == "__main__":
    test_issue_106()
    test_issue_82()
