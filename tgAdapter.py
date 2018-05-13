# -*- coding: utf-8 -*-

# import serial
import time
import telepot
import datetime as dt
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import shutil
import sys
import os
sys.path.insert(0, '..\\')

from danbot import *


TOKEN = ""  # token should be loaded from file
keysPath = "res/keys.json"


toriteli = DanBot()


def handle(msg):

	content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long = True)
	response = toriteli.process_msg(msg, content_type, chat_type, chat_id, date, msg_id)



def main():

	global TOKEN

	TOKEN = readJSON("./res/keys.json")["TOKEN"]

	bot = telepot.Bot(TOKEN)
	print(bot.getMe())
	TOKEN = getKeysData(keysPath, ["TOKEN"])[0]
	toriteli.set_bot(bot)

	MessageLoop(bot, handle).run_as_thread()
	print('Listening ...')

	while 1:
		time.sleep(10)




if __name__ == '__main__':
	main()
