#!/bin/bash

source /home/delom/Projects/noobdanbot/venv/bin/activate

cd /home/delom/Projects/noobdanbot/DanBot2/
git pull
python tg_adapter.py
