# Contributing to _LPSim_

Thanks for you interest in contributing to _lpsim_!

## Prerequisites

_lpsim_ is written in [Python](https://www.python.org/), requires Python>=3.10 to run, so please make sure you have Python>=3.10 installed.

To confirm your Python version, simply run `python --version` or `python3 --version` in terminal ("Terminal" app on macOS or "Windows Terminal" on Windows).

To develop _lpsim_, you'll need to install [git](https://git-scm.com/) for version control, and run:

```
git clone https://github.com/LPSim/backend
cd backend
```

to enter the project folder.

Then, you should create a virtual environment for this project. It's better to keep the dependencies environment isolated.

```
python -m venv venv
source venv/bin/activate
```

Each time you open a new terminal, you should run `source venv/bin/activate` to enter the venv.

## Install _lpsim_ for develpement

> [!WARNING]
> Running `pip install lpsim` or `pip install .` in `backend` folder does not install development dependencies.

Activate venv, enter the `backend` folder you have cloned before, and run `pip install -e ".[dev]"`. This command will install pytest and its plugins. The option `-e` helps you to install an editable version of `lpsim` so that you can import `lpsim` from the `backend` folder locally.

Optionally, you can also run `pip install pre-commit` or `pipx install pre-commit` to install pre-commit for linting and formatting, and run `pre-commit install` to install a pre-commit hook in your **local** repository. After that, each time you commit your changes, pre-commit will run hooks to find typos, do lints and format your codes.

## Running tests

Since @zyr17 writes some test codes in `tests` that refer to each other, we can not simply run `pytest` to run tests. Instead, we need to run `python -m pytest` in `backend` folder, which will add the current directory (`backend` folder) to `sys.path`. More details can be found at [pytest's documentation](https://docs.pytest.org/en/7.2.x/how-to/usage.html#calling-pytest-through-python-m-pytest).
