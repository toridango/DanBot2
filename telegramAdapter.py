# -*- coding: utf-8 -*-

# import serial
import time
import telepot
import datetime as dt
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from getAHK import *
from processSpells import *
import random as rand
import json
import shutil
import os


TOKEN = ""  # token should be loaded from file 
bote = 0
bingoNUM = 512
Passphrase = "Now it's time to start the fun"
firstMsg = True
userList = {}
users = {}
spells = {}
pauseFlag = False



def handle(msg):
    content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long = True)



MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

while 1:
	time.sleep(10)
