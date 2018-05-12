# -*- coding: utf-8 -*-

# import serial
import time
import telepot
import datetime as dt
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import random as rand
import shutil
import os
import sys
sys.path.insert(0, '..\\')

from DanBot import *


TOKEN = ""  # token should be loaded from file
keysPath = "res/keys.json"


toriteli = DanBot(keysPath)


def handle(msg):

    content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long = True)

	response = toriteli.process_msg(msg, content_type, chat_type, chat_id, date, msg_id)



def main():

	global TOKEN

	bot = telepot.Bot(TOKEN)
	print(bot.getMe())
	TOKEN = getKeysData(keysPath, ["TOKEN"])[0]

	MessageLoop(bot, handle).run_as_thread()
	print('Listening ...')

	while 1:
		time.sleep(10)




if __name__ == '__main__':
	main()
