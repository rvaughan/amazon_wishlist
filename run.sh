#!/usr/bin/env bash

if [ ! -d venv ]
then
    python3 -m venv venv
    source ./venv/bin/activate
    pip3 install -r requirements.txt

    deactivate
fi

source ./venv/bin/activate

python main.py
