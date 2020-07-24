#!/bin/sh

cd /home/pi/Projects/noobdanbot/DanBot2/
git pull
x-terminal-emulator -e /usr/bin/python3 tg_adapter.py

cd /home/pi/Projects/noobdanbot/DanBot2/danddanbot/
/usr/bin/python3 danddanbot.py

$SHELL
