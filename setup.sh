#!/usr/bin/env bash

rm -rf movielog.egg-info
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
