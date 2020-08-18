import datetime as dt
import random as rand
import re

from . import db_handler as db
from .modules.gdquote import get_gdquote
from .modules.get_ahk import get_ahk
from .modules.ifc_calendar import get_ifc_string_date
from .modules.process_spells import process_spell
from .modules.jackpot_calculations import calc_expected_coins, calc_expected_coin_volume


def get_ratio(data):
    aux = {}
    msg = ""
    try:
        for user in data:
            data[user]["total"] = float(data[user]["spam"]) + float(data[user]["messages"])
            aux[user] = 100 * float(data[user]["spam"]) / float(data[user]["total"])

        i = 1
        for user in sorted(aux, key=aux.get):
            msg += str(i) + ". " + user + ": " + "{0:.2f}".format(aux[user]) + "%\n"
            i += 1
    except:
        msg = "Wrong formatting or no data found"

    return msg


def get_id_and_callsign(msg):
    ret = str(msg['from']['id']) + " | "
    ret += get_callsign(msg['from'])
    return ret


def get_callsign(msg_from):
    return msg_from.get('username') or msg_from['first_name']


def get_name(msg_from):
    return msg_from.get('first_name') or msg_from['username']


def try_parsing_date(text):
    for fmt in ('%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d'):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


class DanBot:
    def __init__(self, bot):
        # TODO move all these constants to a JSON or smth instead of hardcoding in init
        self.MAX_GROUP_NAME_LEN = 20
        self.BINGO_NUM = 512
        self.COMMENT_THRESH = 0.02
        self.RE_DICT = {
            "date": r"((\d{4})[-\/\.](0?[1-9]|1[012])[-\/\.](3[01]|[12][0-9]|0?[1-9]))|"
                    r"((3[01]|[12][0-9]|0?[1-9])[-\/\.](0?[1-9]|1[012])[-\/\.](\d{4}))",
            "subreddit": r"r/([^\s/]+)"
        }
        self.SUBREDDIT_LEN = 21

        self.strings = db.load_resource("strings")
        self.user_dict = db.load_resource("users")
        self.spells = db.load_resource("spells")
        self.global_data = db.load_resource("global")
        self.quotes = db.get_quotes()

        self.passphrase = self.strings["passphrase"]
        self.default_passphrase = self.strings["default_passphrase"]

        self.debate_mode = False
        self.pause_flag = False

        self.bot = bot

    def preliminary_checks(self, msg):
        update = False

        # Check if member has left
        if 'left_chat_member' in msg.keys():
            print("\nMEMBER LEFT D:")

        # Check if member is new
        if str(msg['from']['id']) not in self.user_dict.keys():
            print("\nNew user: " + get_id_and_callsign(msg))
            self.new_user(msg)
            update = True

        # Check if member has a chat list
        if 'chats' not in self.user_dict[str(msg['from']['id'])]:
            self.user_dict[str(msg['from']['id'])]['chats'] = []
            update = True

        # Check if member has this chat in their list
        if msg['chat']['id'] not in self.user_dict[str(msg['from']['id'])]['chats']:
            self.user_dict[str(msg['from']['id'])]['chats'].append(msg['chat']['id'])
            update = True

        return update

    def new_user(self, msg):
        user_id = str(msg['from']['id'])
        self.user_dict[user_id] = msg['from']
        self.user_dict[user_id]['id'] = str(self.user_dict[user_id]['id'])
        self.user_dict[user_id]["equipment"] = {}
        self.user_dict[user_id]["titles"] = []
        self.user_dict[user_id]["cmdUsage"] = {}
        self.user_dict[user_id]['chats'] = []
        self.user_dict[user_id]['inventory'] = {"coins": 0}
        self.user_dict[user_id]['msg_count'] = 0
        self.user_dict[user_id]['msg_count_before_jackpot'] = 0

    def update_user_field(self, msg, field):
        user = self.user_dict[str(msg['from']['id'])]
        if field in msg["from"]:
            if field in user:
                if user[field] != msg["from"][field]:
                    self.user_dict[str(msg['from']['id'])][field] = msg["from"][field]
                    return True
            else:
                self.user_dict[str(msg['from']['id'])][field] = msg["from"][field]
        return False

    def update_user_names(self, msg):
        update = False

        update = update or self.update_user_field(msg, "first_name")
        update = update or self.update_user_field(msg, "last_name")
        update = update or self.update_user_field(msg, "username")

        return update

    def log_usage(self, user_list, user, command):
        userid = str(user['id'])
        print("UserID:", userid, " Command:", command)
        # print(self.userList)
        # print(self.userList[userid]['cmdUsage'])
        if command in self.user_dict[userid]['cmdUsage']:
            self.user_dict[userid]['cmdUsage'][command] = str(1 + int(self.user_dict[userid]['cmdUsage'][command]))
        else:
            self.user_dict[userid]['cmdUsage'][command] = "1"

        return True

    def add_coins_to_user(self, jackpot, user):
        if "inventory" in self.user_dict[str(user['id'])]:
            if "coins" in self.user_dict[str(user['id'])]["inventory"]:
                self.user_dict[str(user['id'])]["inventory"]["coins"] += jackpot
            else:
                self.user_dict[str(user['id'])]["inventory"]["coins"] = jackpot
        else:
            self.user_dict[str(user['id'])]["inventory"] = {"coins": jackpot}

        return True

    def get_user_coins(self, user):
        if "inventory" not in self.user_dict[str(user['id'])]:
            self.user_dict[str(user['id'])]["inventory"] = {"coins": 0}

        if "coins" not in self.user_dict[str(user['id'])]["inventory"]:
            self.user_dict[str(user['id'])]["inventory"]["coins"] = 0

        return self.user_dict[str(user['id'])]["inventory"]["coins"]

    def callback_markov(self, msg, chat_id, msg_id):
        update = self.log_usage(self.user_dict, msg['from'], "/markov")
        self.bot.deleteMessage((chat_id, msg_id))
        return update

    def callback_help(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/help")
        self.bot.sendMessage(chat_id, self.strings["help"])
        return update

    def callback_greet(self, txt, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], txt)

        if txt == "Hello" or txt == "Hola":
            self.bot.sendMessage(chat_id, txt + " " + get_name(msg['from']))
        elif txt == "Greetings":
            self.bot.sendMessage(chat_id, txt + " " + get_name(msg['from']) + ".\nI am the new Danbot")

        return update

    def callback_getahk(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/getahk")

        if "/getahk@noobdanbot" in msg['text']:
            st = len("/getahk@noobdanbot ")
        else:
            st = len("/getahk ")

        cod = msg['text'][st + 1 - 1:-1]
        frame = "on"

        if len(msg['text']) > len("/getahk"):
            if msg['text'][len("/getahk")] == "!":
                frame = "off"

        try:
            ahk = get_ahk(cod, frame)
            self.bot.sendMessage(chat_id, "AHK code to paste in hotkey:\n```" + ahk + "```", parse_mode="Markdown")
        except:
            self.bot.sendMessage(chat_id, "Error getting AHK code.")

        return update

    def callback_hint(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/hint")
        self.bot.sendMessage(chat_id, self.strings["hint"])
        return update

    def callback_passphrase(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "Passphrase")

        indx = rand.randint(0, len(self.quotes) - 1)
        self.bot.sendMessage(chat_id, self.quotes[indx])

        if self.passphrase == "I'm a Fusion":
            self.passphrase = str(rand.randint(0, 999999999))
        else:
            self.passphrase = "I'm a Fusion!"

        return update

    def callback_spamratio(self, msg, chat_id):
        if msg['text'] == "/spamratio" or msg['text'] == "/spamratio@noobdanbot":
            self.bot.sendMessage(chat_id, self.strings["spamratio_tooltip"])
        else:
            update = self.log_usage(self.user_dict, msg['from'], "/spamratio")

            text = msg['text'][msg['text'].find("<") + 1: msg['text'].find(">")]
            end = False
            i = 1
            users = {}
            while not end:
                if not str(i) + "." in text:
                    end = True
                else:
                    segment = text[text.find(str(i) + ".") + len(str(i) + "."):
                                   text.find(str(i) + ".") + text[text.find(str(i) + "."):].find("\n")]
                    if "(" in segment and ")" in segment:
                        user = segment[segment.find("(") + 1: segment.find(")")]
                    else:
                        user = segment[segment.find(".") + 1 + 1: segment.find(":")]

                    messages = segment[segment.find(":") + 1 + 1: segment.find(",")].strip()
                    spam = segment[segment.find(",") + 1:].strip()

                    users[user] = {"messages": messages, "spam": spam}
                i += 1

            if users == {}:
                ret = "No data found"
            else:
                ret = get_ratio(users)
            self.bot.sendMessage(chat_id, ret)

            return update

    def callback_equip(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/equip")

        max_slot_len = 15
        max_slots = 16
        no_tags = True
        char_exceptions = "+-1234567890"

        if "@noobdanbot" in msg["text"]:
            text = msg['text'][len("/equip@noobdanbot"):].strip()
        else:
            text = msg['text'][len("/equip"):].strip()

        if "<" in text and ">" in text:
            no_tags = False
            slot = text[text.find("<") + len("<"): text.find(">")]
            aux = text[text.find("> ") + len("> "):]
            what = aux[aux.find("<") + len("<"): aux.find(">")]
            char_exceptions += " "
        else:
            slot = text[:text.find(" ")].strip()
            what = text[text.find(" ") + 1:]

        s_aux = slot[:]
        for c in char_exceptions:
            s_aux = s_aux.replace(c, "")

        if no_tags and (" " in slot or len(slot) > max_slot_len or not s_aux.isalpha()):
            self.bot.sendMessage(chat_id,
                                 "The slot can only be one word consisting of 15 alphabetic characters or less.")
        else:
            if not no_tags and (len(slot) > max_slot_len or not s_aux.isalpha()):
                self.bot.sendMessage(chat_id,
                                     "The slot inside tags can consist at most of 15 alphabetic characters or less.")
            else:
                w_aux = what[:]
                for c in "'+-1234567890":
                    w_aux = w_aux.replace(c, "")

                if not w_aux.replace(" ", "").isalpha():
                    self.bot.sendMessage(chat_id,
                                         "Use only alphabetic characters for the item (or null to delete the slot)")
                else:
                    if len(self.user_dict[str(msg['from']['id'])]['equipment']) > max_slots:
                        self.bot.sendMessage(chat_id,
                                             "Maximum number of equipment slots in use (" + str(max_slots) + ")")
                    else:
                        if what == "null":
                            try:
                                del self.user_dict[str(msg['from']['id'])]['equipment'][slot.lower()]
                                update = True
                            except:
                                self.bot.sendMessage(chat_id, "No such slot")
                        else:
                            self.user_dict[str(msg['from']['id'])]['equipment'][slot.lower()] = what
                            update = True

        return update

    def callback_delequip(self, msg, chat_id):
        update = False
        text = msg['text'][len("/equip"):].strip()

        if "<" not in text and ">" not in text:
            self.bot.sendMessage(chat_id, "Type the name of the slot to delete between tags: <slotname>")
        else:
            slot = text[text.find("<") + len("<"): text.find(">")]

            try:
                del self.user_dict[str(msg['from']['id'])]['equipment'][slot.lower()]
                update = self.log_usage(self.user_dict, msg['from'], "/delequip")
            except:
                self.bot.sendMessage(chat_id, "No such slot")

        return update

    def callback_showequip(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/showequip")

        equip = ""
        for key in self.user_dict[str(msg['from']['id'])]['equipment']:
            if self.user_dict[str(msg['from']['id'])]['equipment'][key] != "":
                equip += key.title() + ": " + self.user_dict[str(msg['from']['id'])]['equipment'][key] + "\n"
        if equip != "":
            self.bot.sendMessage(chat_id, equip)
        else:
            self.bot.sendMessage(chat_id, "You are not wearing anything ( ͡° ͜ʖ ͡°)")

        return update

    def callback_cast(self, msg, chat_id):
        update = False
        spell, effect = process_spell(self.spells, msg['from'], msg['text'])

        if spell != "wrong" and effect != "wrong":
            self.bot.sendMessage(chat_id, effect)
            update = self.log_usage(self.user_dict, msg['from'], spell)

        return update

    # unicode lower case comparison
    def ulower(self, s1, s2):
        pass

    def users_in_group(self, group, chat_id):
        users = []
        for key in self.user_dict:
            if "chats" in self.user_dict[key]:
                if chat_id in self.user_dict[key]["chats"]:
                    if "groups" in self.user_dict[key]:
                        found = (group.lower() == "everyone")
                        i = 0
                        while not found and i < len(self.user_dict[key]["groups"]):
                            if group.lower() == self.user_dict[key]["groups"][i].lower():
                                found = True
                            i += 1
                        if found:
                            users.append(key)
                    else:
                        self.user_dict[key]["groups"] = []

        return users

    def callback_newjoin(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/join")

        group = msg["text"][len("/join "):].strip()

        if group != "":
            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:group.find(" ")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:self.MAX_GROUP_NAME_LEN]

            if group == self.strings["no_groups"]:
                self.bot.sendMessage(chat_id, self.strings["that_wont_work"][
                    rand.randint(0, len(self.strings["that_wont_work"]) - 1)])
            else:
                if "groups" in self.user_dict[str(msg["from"]["id"])]:
                    if group not in self.user_dict[str(msg["from"]["id"])]["groups"]:
                        self.user_dict[str(msg["from"]["id"])]["groups"].append(group)
                else:
                    self.user_dict[str(msg["from"]["id"])]["groups"] = [group]

        else:
            self.bot.sendMessage(chat_id, self.strings["join_tooltip"])

        return update

    def callback_newleave(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/join")

        group = msg["text"][len("/leave "):].strip()

        if group != "":
            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:group.find(" ")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:self.MAX_GROUP_NAME_LEN]

            if "groups" in self.user_dict[str(msg["from"]["id"])]:
                some_left = True
                while some_left:
                    if group in self.user_dict[str(msg["from"]["id"])]["groups"]:
                        self.user_dict[str(msg["from"]["id"])]["groups"].remove(group)
                    else:
                        some_left = False
            else:
                self.user_dict[str(msg["from"]["id"])]["groups"] = [group]

        else:
            self.bot.sendMessage(chat_id, self.strings["leave_tooltip"])

        return update

    def callback_shoutouts(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/shoutouts")

        group = msg["text"][len("/shoutouts "):].strip()
        message = ""

        if group != "":
            if "\n" in group:
                group = group[:group.find("\n")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:group.find(" ")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:self.MAX_GROUP_NAME_LEN]

            empty = True
            for userID in self.users_in_group(group, chat_id):
                empty = False
                if "username" in self.user_dict[userID]:
                    message += "@{} ".format(self.user_dict[userID]["username"], userID)
                else:
                    message += "[{}](tg://user?id={}) ".format(self.user_dict[userID]["first_name"], userID)

            if empty:
                message = "Empty group"

            self.bot.sendMessage(chat_id, message, parse_mode="Markdown", reply_to_message_id=msg["message_id"])

        else:
            self.bot.sendMessage(chat_id, self.strings["shoutouts_tooltip"])

        return update

    def callback_lsgroups(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/lsgroups")
        if len(self.user_dict[str(msg["from"]["id"])]["groups"]) > 0:
            self.bot.sendMessage(chat_id, ", ".join(self.user_dict[str(msg["from"]["id"])]["groups"]))
        else:
            self.bot.sendMessage(chat_id, self.strings["no_groups"])
        return update

    # if rand.random() is below comment_threshold, it sends a comment (from strings["comments"])
    # meaning that 1 is always, 0 is never
    def callback_edit_thresh(self, msg):
        if len(msg['text'].split(" ")[1]) == 3:
            try:
                ret = int(msg['text'].split(" ")[1])
            except:
                ret = self.COMMENT_THRESH

        # TODO when can len != 3? it will explode in the return because ret not defined
        return ret

    def callback_laugh_along(self, chat_id):
        laughs = self.strings["laughs"]
        if rand.random() < 0.1:
            self.bot.sendMessage(chat_id, laughs[rand.randint(0, len(laughs) - 1)])

    def callback_ifc(self, msg, chat_id):
        update = self.log_usage(self.user_dict, msg['from'], "/ifc")

        txt = msg["text"]

        if txt == "/ifc" or txt == "/ifc@noobdanbot":
            today = dt.date.today()
            self.bot.sendMessage(chat_id, get_ifc_string_date(today.day, today.month, today.year))
            return update
        else:
            date_str = txt[len("/ifc ") + 1: len("/ifc ") + 1 + 10 + 1].strip()
            if len(date_str) in [10, 9, 8] and re.match(self.RE_DICT["date"], date_str):
                try:
                    date = try_parsing_date(date_str)
                    self.bot.sendMessage(chat_id, get_ifc_string_date(date.day, date.month, date.year))
                    return update
                except ValueError:
                    failed = True
            else:
                failed = True

        if failed:
            self.bot.sendMessage(chat_id, self.strings["ifc_tooltip"])

    def callback_subreddit(self, msg, chat_id):
        txt = msg['text']

        message = ""
        for subr in re.findall(self.RE_DICT["subreddit"], txt):
            if len(subr) <= self.SUBREDDIT_LEN:
                message += "[r/{}](https://reddit.com/r/{}) ".format(subr, subr)

        if message != "":
            self.bot.sendMessage(chat_id, message, parse_mode="Markdown", disable_web_page_preview=True)

    def callback_gdquote(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/gdquote")
        self.bot.sendMessage(chat_id, get_gdquote())

    def callback_debatemode(self, msg, chat_id):
        usage_msg = "Usage: /debatemode [on|off]"
        self.log_usage(self.user_dict, msg['from'], "/debatemode")
        args = msg['text'].split(" ")
        if len(args) != 2:
            self.bot.sendMessage(chat_id, usage_msg)
        else:
            switch = args[1]
            if switch == "on":
                self.debate_mode = True
            elif switch == "off":
                self.debate_mode = False
            else:
                self.bot.sendMessage(chat_id, usage_msg)

    def callback_showcoins(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/showcoins")

        name = get_callsign(msg['from'])
        coins = self.get_user_coins(msg['from'])

        self.bot.sendMessage(chat_id, f"{name} has {coins} coins.")

    def callback_msgcount(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/msgcount")

        name = get_callsign(msg['from'])
        messages = self.user_dict[str(msg["from"]["id"])]["msg_count"]

        reply = f"{name} has sent a total of {messages} messages accross all DanBot groups."

        self.bot.sendMessage(chat_id, reply)

    def get_total_messages_sent(self, after_jackpot=False):
        total_msg = sum(user["msg_count"] for user in self.user_dict.values())

        if after_jackpot:
            total_msg_before_jackpot = sum(user["msg_count_before_jackpot"] for user in self.user_dict.values())
            return total_msg - total_msg_before_jackpot
        else:
            return total_msg

    def get_total_coins(self):
        return sum(self.get_user_coins(user) for user in self.user_dict.values())

    def callback_luck(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/luck")

        user_id = str(msg["from"]["id"])

        name = get_callsign(msg['from'])
        user_msg_total = self.user_dict[user_id]["msg_count"]
        user_msg_after_jackpot = user_msg_total - self.user_dict[user_id]["msg_count_before_jackpot"]

        global_msg_total = self.get_total_messages_sent(after_jackpot=True)
        ratio = user_msg_after_jackpot / global_msg_total

        current_coins = self.user_dict[user_id]["inventory"]["coins"]
        expected_coins = calc_expected_coins(global_msg_total, user_msg_after_jackpot, 1 - 1 / self.BINGO_NUM)

        if user_msg_after_jackpot == 0 or current_coins == 0:
            reply = ""

        luck_percentage = 100 * (current_coins - expected_coins) / expected_coins
        lucky_str = "LUCKY" if luck_percentage > 0 else "UNLUCKY"

        lucky_percentage_norm = luck_percentage - self.get_average_users_luck()
        lucky_str_norm = "LUCKY" if lucky_percentage_norm > 0 else "UNLUCKY"

        reply = f"Since jackpot was enabled:\n" \
                f"{name} has sent {user_msg_after_jackpot} messages.\n" \
                f"A total of {global_msg_total} messages have been sent by all users.\n" \
                f"As such, {name} has sent {100 * ratio:.2f}% of all messages.\n" \
                f"After performing advanced AI probabilistic calculations, I believe that...\n" \
                f"*{name} deserves to have {int(expected_coins)} coins.*\n" \
                f"Currently, {name} has {current_coins} coins. Thus, I conclude that...\n" \
                f"*{name} is {abs(luck_percentage):.2f}% more {lucky_str} than average.*\n" \
                f"However, taking into account the average luck of DanBot users, I conclude that...\n" \
                f"*{name} is {abs(lucky_percentage_norm):.2f}% more {lucky_str_norm} than other DanBot users.*\n"

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def get_average_users_luck(self):
        global_msg_total = self.get_total_messages_sent(after_jackpot=True)

        total_coins = self.get_total_coins()
        expected_coins = calc_expected_coin_volume(global_msg_total, 1 - 1 / self.BINGO_NUM)

        luck_percentage = 100 * (total_coins - expected_coins) / expected_coins

        return luck_percentage

    def callback_coin_volume(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/coinvolume")

        total_coins = self.get_total_coins()
        global_msg_total = self.get_total_messages_sent(after_jackpot=True)
        expected_coins = calc_expected_coin_volume(global_msg_total, 1 - 1 / self.BINGO_NUM)

        luck_percentage = self.get_average_users_luck()
        lucky_str = "LUCKY" if luck_percentage > 0 else "UNLUCKY"

        reply = f"Current coin volume: {total_coins}\n" \
                f"Expected coin volume: {int(expected_coins)}\n" \
                f"In average, DanBot users are {abs(luck_percentage):.2f}% more {lucky_str} than average."

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def callback_jackpot(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/jackpot")
        reply = f"Currenly, the jackpot is at {self.global_data['jackpot']} coins."
        self.bot.sendMessage(chat_id, reply)

    def get_user_luck(self, user_id):
        global_msg_total = self.get_total_messages_sent(after_jackpot=True)
        user_msg_total = self.user_dict[user_id]["msg_count"]
        user_msg_after_jackpot = user_msg_total - self.user_dict[user_id]["msg_count_before_jackpot"]
        current_coins = self.user_dict[user_id]["inventory"]["coins"]
        expected_coins = calc_expected_coins(global_msg_total, user_msg_after_jackpot, 1 - 1 / self.BINGO_NUM)

        if user_msg_after_jackpot == 0 or current_coins == 0:
            return None

        luck_percentage = 100 * (current_coins - expected_coins) / expected_coins

        return luck_percentage

    def get_user_callsign(self, user_id):
        user = self.user_dict[user_id]
        return user.get('username') or user['first_name']

    def make_top(self, get_attr, percentage=True):
        top = []
        for user_id in self.user_dict:
            user = self.get_user_callsign(user_id)
            luck = get_attr(user_id)
            if luck is not None:
                top.append([user, luck])

        top.sort(key=lambda t: t[1], reverse=True)

        if percentage:
            total = sum(t[1] for t in top)
            for t in top:
                t.append(100 * t[1] / total)

        return top

    @staticmethod
    def get_std_top_str(top):
        top_str = "\n".join(f"{user + ':':<12} {count}\t({ratio:.2f}%)" for user, count, ratio in top)
        return "```\n" + top_str + "\n```"

    def callback_topluck(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/topluck")

        top = self.make_top(lambda uid: self.get_user_luck(uid), percentage=False)
        reply = "Luck ranking:\n\n" \
                + "```\n" \
                + "\n".join(f"{user + ':':<12} {luck:.2f}%" for user, luck in top) \
                + "\n```"

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def callback_topmsg(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/topmsg")

        top = self.make_top(lambda uid: self.user_dict[uid]["msg_count"] or None)
        reply = "Messages sent ranking:\n\n" + self.get_std_top_str(top)

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def callback_topmsg_jackpot(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/topmsg_jackpot")

        def get_attr(uid):
            count = self.user_dict[uid]["msg_count"] - self.user_dict[uid]["msg_count_before_jackpot"]
            return count or None

        top = self.make_top(get_attr)
        reply = "Messages sent after jackpot ranking:\n\n" + self.get_std_top_str(top)

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def callback_topcoins(self, msg, chat_id):
        self.log_usage(self.user_dict, msg['from'], "/topcoins")

        top = self.make_top(lambda uid: self.user_dict[uid]["inventory"]["coins"] or None)
        reply = "Coins owned ranking:\n\n" + self.get_std_top_str(top)

        self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def callback_investigate_fraud(self, msg, chat_id):
        self.bot.sendMessage(chat_id, "DanBot Police is now investigating jackpot fraud...")

        if not self.global_data["fraud"]:
            self.bot.sendMessage(chat_id, "*No instances of jackpot fraud have been found.*", parse_mode="Markdown")
            return

        jackpots_after_update = [j for j in self.global_data["bingo_stats"] if j["user"] is not None]

        offenders = {}
        corrected_jackpots = []

        for i in range(1, len(jackpots_after_update)):
            prev_jackpot = jackpots_after_update[i - 1]
            curr_jackpot = jackpots_after_update[i]
            proper_jackpot_coins = curr_jackpot["coins"] - prev_jackpot["coins"]
            user = curr_jackpot["user"]
            if user not in offenders:
                offenders[user] = []
            offenders[user].append((curr_jackpot["coins"], proper_jackpot_coins))
            corrected_jackpots.append(proper_jackpot_coins)

        # correct current jackpot
        self.global_data["jackpot"] -= jackpots_after_update[-1]["coins"]

        # correct jackpot stats
        index_offset = len(self.global_data["bingo_stats"]) - len(jackpots_after_update) + 1
        for i in range(len(corrected_jackpots)):
            self.global_data["bingo_stats"][index_offset + i]["coins"] = corrected_jackpots[i]

        # correct user coins
        for user, offences in offenders.items():
            username = self.get_user_callsign(user)
            reply = f"*{username} has been found guilty of fraud!*\n\n"
            total_fraud_coins = 0
            for actual_coins, proper_coins in offences:
                reply += f"- Received a jackpot valued in {actual_coins} coins, when it should have been {proper_coins} coins.\n"
                total_fraud_coins += actual_coins - proper_coins
            reply += f"\n*As such, DanBot Police will confiscate {total_fraud_coins} coins from {username}.*\n\n"
            reply += f"{username}'s coin balance was {self.user_dict[user]['inventory']['coins']}"
            self.user_dict[user]['inventory']['coins'] -= total_fraud_coins
            reply += f", but after the intervention it has been reduced to {self.user_dict[user]['inventory']['coins']} coins."
            self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

        self.global_data["fraud"] = False
        self.bot.sendMessage(chat_id, "*All instances of jackpot fraud have been corrected.*", parse_mode="Markdown")

    def process_msg(self, msg, content_type, chat_type, chat_id, date, msg_id):
        trolls = []
        self.preliminary_checks(msg)
        prob = rand.randint(1, self.BINGO_NUM)
        is_edit = "edit_date" in msg

        if not is_edit:
            self.global_data["jackpot"] += 1
            self.user_dict[str(msg["from"]["id"])]["msg_count"] += 1

        if content_type == "text" and msg['text'][:len("/yamete")] == "/yamete":
            print("\nTaking a break...")
            self.pause_flag = True
        elif content_type == "text" and msg['text'][:len("/tsudzukete")] == "/tsudzuite":
            print("\nCarrying on...")
            self.pause_flag = False

        if msg['from']["is_bot"]:
            print(f"\nI see a bot: username {msg['from']['username']}, first_name {msg['from']['first_name']}")
        else:
            self.update_user_names(msg)

        if content_type == 'text' and not self.pause_flag and not msg['from']['id'] in trolls:
            if msg['text'].startswith("/markdown"):
                self.bot.deleteMessage((chat_id, msg_id))
                self.bot.sendMessage(chat_id, msg['text'][len("/markdown "):], parse_mode="Markdown")

            elif msg['text'][:len('/markov')] == "/markov":
                self.callback_markov(msg, chat_id, msg_id)

            elif msg['text'] in ['/help', '/help@noobdanbot']:
                self.callback_help(msg, chat_id)

            elif msg['text'] == "Hello Danbot":
                self.callback_greet("Hello", msg, chat_id)

            elif msg['text'] == "Hola Danbot":
                self.callback_greet("Hola", msg, chat_id)

            elif msg['text'] == "Greetings Danbot":
                self.callback_greet("Greetings", msg, chat_id)

            elif msg['text'][:len('/getahk')] == '/getahk':
                self.callback_getahk(msg, chat_id)

            elif msg['text'][:len("/hint")] == "/hint":
                self.callback_hint(msg, chat_id)

            elif self.passphrase in msg['text']:
                self.callback_passphrase(msg, chat_id)

            elif msg['text'][:len('/spamratio')] == "/spamratio":
                self.callback_spamratio(msg, chat_id)

            elif msg['text'][:len('/equip')] == "/equip":
                self.callback_equip(msg, chat_id)

            elif msg['text'][:len('/delequip')] == "/delequip":
                self.callback_delequip(msg, chat_id)

            elif msg['text'][:len('/showequip')] == "/showequip":
                self.callback_showequip(msg, chat_id)

            elif msg['text'][:len('Cast ')].lower() == "cast " or \
                    msg['text'][:len('Sing ')].lower() == "sing " or \
                    msg['text'][:len('Pray for ')].lower() == "pray for ":
                self.callback_cast(msg, chat_id)

            elif msg['text'].lower() == "danbot":
                self.bot.sendMessage(chat_id, ["What?", "Nani?"][rand.randint(0, 1)])
            elif msg['text'].lower() in ["ダンボト", "暖ボト"]:
                self.bot.sendMessage(chat_id, "何？")
            elif msg['text'].lower() in ["お前はもう死んでいる"]:
                self.bot.sendMessage(chat_id, "What a weeb")

            elif msg['text'] in self.strings["laugh_triggers"] and not is_edit and not self.debate_mode:
                self.callback_laugh_along(chat_id)

            elif msg['text'].startswith("/join"):
                self.callback_newjoin(msg, chat_id)

            elif msg['text'].startswith("/leave"):
                self.callback_newleave(msg, chat_id)

            elif msg['text'].startswith("/shoutouts") and not is_edit:
                self.callback_shoutouts(msg, chat_id)

            elif msg['text'].startswith("/everyone") and not is_edit:
                msg["text"] = "/shoutouts <everyone>"
                self.callback_shoutouts(msg, chat_id)

            elif msg['text'].startswith("/lsgroups"):
                self.callback_lsgroups(msg, chat_id)

            elif msg['text'].lower().startswith("/ifc"):
                self.callback_ifc(msg, chat_id)

            elif msg['text'].startswith("r/"):
                self.callback_subreddit(msg, chat_id)

            elif msg['text'].lower().startswith("danbot say something") \
                    or msg['text'].lower().startswith("say something danbot"):
                aggregate = self.strings["comments"] + self.strings["that_wont_work"]
                if self.debate_mode:
                    aggregate += ["please disable debate mode"]
                self.bot.sendMessage(chat_id, aggregate[rand.randint(0, len(aggregate) - 1)])

            elif msg['text'].lower().startswith("/gdquote"):
                self.callback_gdquote(msg, chat_id)

            elif msg['text'].lower().startswith("/debatemode"):
                self.callback_debatemode(msg, chat_id)

            elif msg['text'].lower().startswith("/showcoins"):
                self.callback_showcoins(msg, chat_id)

            elif msg['text'].lower().startswith("/msgcount"):
                self.callback_msgcount(msg, chat_id)

            elif msg['text'].lower().startswith("/luck"):
                self.callback_luck(msg, chat_id)

            elif msg['text'].lower().startswith("/coinvolume"):
                self.callback_coin_volume(msg, chat_id)

            elif msg['text'].lower().startswith("/jackpot"):
                self.callback_jackpot(msg, chat_id)

            elif msg['text'].lower().startswith("/topluck"):
                self.callback_topluck(msg, chat_id)

            elif msg['text'].lower().startswith("/topmsg_jackpot"):
                self.callback_topmsg_jackpot(msg, chat_id)

            elif msg['text'].lower().startswith("/topmsg"):
                self.callback_topmsg(msg, chat_id)

            elif msg['text'].lower().startswith("/topcoins"):
                self.callback_topcoins(msg, chat_id)

            elif msg['text'].lower().startswith("/investigate_fraud"):
                self.callback_investigate_fraud(msg, chat_id)

        if prob == self.BINGO_NUM and not is_edit:
            jackpot = self.global_data["jackpot"]
            print(f"\nBINGO! After {jackpot} messages")
            self.global_data["bingo_stats"].append({"coins": jackpot, "user": str(msg['from']['id'])})
            self.add_coins_to_user(jackpot, msg['from'])
            self.global_data["jackpot"] = 0
            name = get_callsign(msg['from'])
            self.bot.sendMessage(chat_id, f"{name} just won the jackpot of {jackpot} coins++ !!!".upper())

        if rand.random() < self.COMMENT_THRESH and not self.debate_mode:
            r = rand.randint(0, len(self.strings["comments"]) - 1)
            self.bot.sendMessage(chat_id, self.strings["comments"][r])

        db.save_resource("users", self.user_dict)
        db.save_resource("global", self.global_data)


def main():
    pass


if __name__ == '__main__':
    main()
