import os
from tests.utils_for_test import do_log_tests


def test_lynette():
    json_fname = "test_lynette.json"
    json_path = os.path.join(os.path.dirname(__file__), "jsons", json_fname)
    do_log_tests(json_path, omnipotent=False)


if __name__ == "__main__":
    test_lynette()
