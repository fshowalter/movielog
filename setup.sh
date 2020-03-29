#!/usr/bin/env bash

brew bundle
rm -rf ./.venv
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
