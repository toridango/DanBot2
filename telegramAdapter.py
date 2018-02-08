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
import shutil
import os


import json


TOKEN = ""  # token should be loaded from file 
keysPath = "res/keys.json"

bote = 0
bingoNUM = 512
Passphrase = "Now it's time to start the fun"
firstMsg = True
userList = {}
users = {}
spells = {}
pauseFlag = False


# Reads json from filepath and returns the unadultered read contents
def readJson(filepath):

	with open(filepath, 'r') as f:
		data = json.load(f)

	return data



# gets the data from the json key data file and returns the target parameter
def getKeysData(filepath, target):

	data = readJson(filepath)

	if target in data:
		target_value = data[target]
	else:
		target_value = None

	return target_value




def handle(msg):
    content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long = True)



def main():

	global TOKEN

	TOKEN = getKeysData(keysPath, "TOKEN")

	MessageLoop(bot, handle).run_as_thread()
	print('Listening ...')

	while 1:
		time.sleep(10)







if __name__ == '__main__':
	main()