#!/usr/bin/env bash

rm -rf movielog.egg-info
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
