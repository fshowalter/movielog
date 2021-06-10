#!/usr/bin/env bash

brew bundle
rm -rf movielog.egg-info
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
mypy --install-types
