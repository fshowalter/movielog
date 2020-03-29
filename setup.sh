#!/usr/bin/env bash

brew bundle
rm -rf ./.venv
rm -rf movielog.egg-info
python3 -m venv ./.venv
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
source ./.venv/bin/activate
poetry install
pip install -e .
