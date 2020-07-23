import time

import telepot
from telepot.loop import MessageLoop

from danbot import DanBot
from danbot import db_handler as db

KEYS_PATH = "res/keys.json"


def handle(msg, danbot):
    content_type, chat_type, chat_id, date, msg_id = telepot.glance(msg, long=True)
    danbot.process_msg(msg, content_type, chat_type, chat_id, date, msg_id)


def main():
    token = db.load_resource("keys")["TOKEN"]
    bot = telepot.Bot(token)
    print(bot.getMe())
    toriteli = DanBot(bot)

    MessageLoop(bot, lambda msg: handle(msg, danbot=toriteli)).run_as_thread()
    print('Listening ...')

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
