import sys
import time

import telepot
from telepot.loop import MessageLoop

# TODO this should never be needed
sys.path.insert(0, '..\\')

from danbot import DanBot
from dbHandler import get_keys_data, read_json

TOKEN = ""  # token should be loaded from file
keysPath = "res/keys.json"

toriteli = DanBot()


def handle(msg):
    content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long=True)
    response = toriteli.process_msg(msg, content_type, chat_type, chat_id, date, msg_id)


def main():
    global TOKEN

    TOKEN = read_json("./res/keys.json")["TOKEN"]

    bot = telepot.Bot(TOKEN)
    print(bot.getMe())
    TOKEN = get_keys_data(keysPath, ["TOKEN"])[0]
    toriteli.set_bot(bot)

    MessageLoop(bot, handle).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(10)


if __name__ == '__main__':
    main()
