#!/usr/bin/env bash

# use the version of npm specified in package.json engines field.
npm install -g npm@$(node -p -e "require('./package.json').engines.npm")