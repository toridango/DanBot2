#!/bin/sh
cd /home/pi/Projects/noobdanbot/DanBot2/
git pull
x-terminal-emulator -e python3 tgAdapter.py

cd /discord/danddanbot/
python3 danddanbot.py

$SHELL