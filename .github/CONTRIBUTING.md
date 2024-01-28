# Contributing to LPSim

## Prerequisites

`lpsim` is written in Python, requires Python >= 3.10 to run.

You'll need to install Python for development and install `pre-commit` to run validations.

```sh
pipx install pre-commit

pre-commit install
```

## Development

You'll need to install an editable version of `lpsim` to develop this project:

```sh
pip install -e ".[dev]"
```

This helps you install `setuptools_scm` and `pytest`.
