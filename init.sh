#!/usr/bin/env bash

if [[ ! -x "$(command -v brew)" ]]; then
    brew install libyaml
fi

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

touch `git rev-parse --show-toplevel`/env.yml
