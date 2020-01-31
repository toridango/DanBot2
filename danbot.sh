#!/bin/sh
cd /home/pi/Projects/noobdanbot/DanBot2/
git pull
x-terminal-emulator -e /usr/bin/python3 tgAdapter.py

cd /home/pi/Projects/noobdanbot/DanBot2/discord/danddanbot/
/usr/bin/python3 danddanbot.py

$SHELL