#!/usr/bin/env bash
set -eu
set -e pipefail

pip install tox poetry

# Enable a local venv for this project so that IDEs can pick it up easily (VSCode)
poetry config virtualenvs.in-project true --local

# Create the local venv and install it
poetry install

# Activate the pre-commit hook in the venv
poetry run pre-commit install --hook-type commit-msg

poetry shell
