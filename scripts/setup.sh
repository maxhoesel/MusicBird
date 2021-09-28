#!/usr/bin/env bash
set -eu
set -e pipefail

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python3 -m pip install 'gitlint>=0.15.0,<0.16.0' 'autopep8'
python3 -m pip install --editable '.[dev]'

gitlint install-hook

# Initialize tox venvs
tox -l > /dev/null
