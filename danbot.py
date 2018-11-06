# -*- coding: utf-8 -*-

import random as rand
import sys
import datetime as dt
import re
reload(sys)
sys.setdefaultencoding("utf-8")

from processSpells import *
from dbHandler import *
from getAHK import *
from IFC_Calendar import getIFCStringDate
from GDQuote import get_GDQuote



def getRatio(data):
    aux = {}
    msg = ""
    try:
        for user in data:
            data[user]["total"] = float(data[user]["spam"]) + float(data[user]["messages"])
            aux[user] = 100 * float(data[user]["spam"]) / float(data[user]["total"])

        i = 1
        for user in sorted(aux, key=aux.get):
            msg += str(i)+". "+user+": "+"{0:.2f}".format(aux[user])+"%\n"
            i += 1
    except:
        msg = "Wrong formatting or no data found"

    return msg

def getID_and_callsign(msg):

    ret = str(msg['from']['id']) + " | "
    ret += get_callsign(msg['from'])
    return ret


def get_callsign(msg_from):

    try:
        ret = msg_from['username']
        # print self.userList.keys()
    except:
        ret =  msg_from['first_name']
        # print self.userList.keys()
    return ret

def get_name(msg_from):

    try:
        ret = msg_from['first_name']
        # print self.userList.keys()
    except:
        ret = msg_from['username']
        # print self.userList.keys()
    return ret



def try_parsing_date(text):
    for fmt in ('%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d'):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')







class DanBot():

    def __init__(self):

        self.strings = readJSON("./res/strings/en-Uk/strings.json")
        self.quotes = getQuotes('./res/Quotes.txt')

        self.MAX_GROUP_NAME_LEN = 20
        self.bingoNUM = 512
        self.bingo_data = readBingo('./res/bingo_'+str(self.bingoNUM)+'.txt')
        self.comment_thresh = 0.02

        self.passphrase = self.strings["passphrase"]
        self.default_passphrase = self.strings["default_passphrase"]

        self.user_path = "./res/users.json"
        self.userList = readJSON(self.user_path)

        self.spell_path = './res/strings/en-Uk/spells.json'
        self.spells = readJSON(self.spell_path)
        self.pauseFlag = False

        self.reDict = {"date":r"((\d{4})[-\/\.](0?[1-9]|1[012])[-\/\.](3[01]|[12][0-9]|0?[1-9]))|((3[01]|[12][0-9]|0?[1-9])[-\/\.](0?[1-9]|1[012])[-\/\.](\d{4}))"}

        self.subRRegex = re.compile(r"\A\s*[\d\.]+\w{0,3}\s*\Z")
        self.subRLen = 21

        self.debatemode = False


    def set_bot(self, bot):

        self.bot = bot



    def preliminary_checks(self, msg):

        update = False

        # Check if member has left
        if 'left_chat_member' in msg.keys():
            print "MEMBER LEFT D:"

        # Check if member is new
        if str(msg['from']['id']) not in self.userList.keys():
            print("New user: " + getID_and_callsign(msg))
            self.new_user(msg)
            update = True

        # Check if member has a chat list
        if 'chats' not in self.userList[str(msg['from']['id'])]:
            self.userList[str(msg['from']['id'])]['chats'] = []
            update = True

        # Check if member has this chat in their list
        if msg['chat']['id'] not in self.userList[str(msg['from']['id'])]['chats']:
            self.userList[str(msg['from']['id'])]['chats'].append(msg['chat']['id'])
            update = True

        return update


    def new_user(self, msg):
        self.userList[str(msg['from']['id'])] = msg['from']
        self.userList[str(msg['from']['id'])]['id'] = str(self.userList[str(msg['from']['id'])]['id'])
        self.userList[str(msg['from']['id'])]["equipment"] = {}
        self.userList[str(msg['from']['id'])]["titles"] = []
        self.userList[str(msg['from']['id'])]["cmdUsage"] = []
        self.userList[str(msg['from']['id'])]['chats'] = []
        self.userList[str(msg['from']['id'])]['inventory'] = {"coins": 0}

    def updateUserField(self, msg, field):
        user = self.userList[str(msg['from']['id'])]
        if field in msg["from"]:
            if field in user:
                if user[field] != msg["from"][field]:
                    self.userList[str(msg['from']['id'])][field] = msg["from"][field]
                    return True
            else:
                self.userList[str(msg['from']['id'])][field] = msg["from"][field]
        return False

    def updateUserNames(self, msg):
        update = False
        str_id = str(msg['from']['id'])
        user = self.userList[str_id]

        update = update or self.updateUserField(msg, "first_name")
        update = update or self.updateUserField(msg, "last_name")
        update = update or self.updateUserField(msg, "username")

        return update



    def logUsage(self, userList, user, command):
        userid = str(user['id'])
        if command in self.userList[userid]['cmdUsage']:
            self.userList[userid]['cmdUsage'][command] = str(1+int(self.userList[userid]['cmdUsage'][command]))
        else:
            self.userList[userid]['cmdUsage'][command] = "1"

        return True

    def addCoinsToUser(self, jackpot, user):
        if "inventory" in self.userList[str(user['id'])]:
            if "coins" in self.userList[str(user['id'])]["inventory"]:
                self.userList[str(user['id'])]["inventory"]["coins"] += jackpot
            else:
                self.userList[str(user['id'])]["inventory"]["coins"] = jackpot
        else:
            self.userList[str(user['id'])]["inventory"] = {"coins": jackpot}

        return True



    def callback_markov(self, msg, chat_id, msg_id):

        update = self.logUsage(self.userList, msg['from'], "/markov")
        self.bot.deleteMessage((chat_id, msg_id))
        return update


    def callback_help(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "/help")
        self.bot.sendMessage(chat_id, self.strings["help"])
        return update

    def callback_greet(self, txt, msg, chat_id):

        if txt == "Hello" or txt == "Hola":
            update = self.logUsage(self.userList, msg['from'], txt)
            self.bot.sendMessage(chat_id, txt + " " + get_name(msg['from']))

        elif txt == "Greetings":
            update = self.logUsage(self.userList, msg['from'], txt)
            self.bot.sendMessage(chat_id, txt + " " + get_name(msg['from']) + ".\nI am the new Danbot")

        return update

    def callback_getahk(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "/getahk")

        if "/getahk@noobdanbot" in msg['text']:
            st = len("/getahk@noobdanbot ")
        else:
            st = len("/getahk ")

        cod = msg['text'][st+1-1:-1]
        frame = "on"

        if len(msg['text']) > len("/getahk"):
            if msg['text'][len("/getahk")] == "!":
                frame = "off"

        try:
            ahk = getAHK(cod, frame)
            self.bot.sendMessage(chat_id, "AHK code to paste in hotkey:\n```"+ahk+"```", parse_mode = "Markdown")
        except:
            self.bot.sendMessage(chat_id, "Error getting AHK code.")

        return update

    def callback_hint(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "/hint")
        self.bot.sendMessage(chat_id, self.strings["hint"])
        return update

    def callback_passphrase(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "Passphrase")

        indx = rand.randint(0,len(self.quotes)-1)
        self.bot.sendMessage(chat_id, self.quotes[indx])

        if self.passphrase == "I'm a Fusion":
            self.passphrase = str(rand.randint(0,999999999))
        else:
            self.passphrase = "I'm a Fusion!"


    def callback_spamratio(self, msg, chat_id):

        if (msg['text'] == "/spamratio" or msg['text'] == "/spamratio@noobdanbot"):

            self.bot.sendMessage(chat_id, self.strings["spamratio_tooltip"])

        else:
            update = self.logUsage(self.userList, msg['from'], "/spamratio")

            text = msg['text'][ msg['text'].find("<")+1 : msg['text'].find(">") ]
            end = False
            i = 1
            users = {}
            while not end:
                if not str(i)+"." in text:
                    end = True
                else:
                    segment = text[ text.find(str(i)+".")+len(str(i)+".") : text.find(str(i)+".") + text[text.find(str(i)+".") : ].find("\n") ]
                    if "(" in segment and ")" in segment:
                        user = segment[segment.find("(")+1 : segment.find(")")]
                    else:
                        user = segment[segment.find(".")+1+1 : segment.find(":")]

                    messages = segment[segment.find(":")+1+1 : segment.find(",")].strip()
                    spam = segment[segment.find(",")+1 : ].strip()

                    users[user] = {"messages":messages, "spam":spam}
                i += 1

            if users == {}:
                ret = "No data found"
            else:
                ret = getRatio(users)
            self.bot.sendMessage(chat_id, ret)

            return update


    def callback_equip(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "/equip")

        maxSlotLen = 15
        maxSlots = 16
        noTags = True
        charExceptions = "+-1234567890"

        if "@noobdanbot" in msg["text"]:
            text = msg['text'][len("/equip@noobdanbot"):].strip()
        else:
            text = msg['text'][len("/equip"):].strip()

        if "<" in text and ">" in text:
            noTags = False
            slot = text[text.find("<")+len("<") : text.find(">")]
            aux = text[text.find("> ") + len("> ") :]
            what = aux[aux.find("<")+len("<") : aux.find(">")]
            charExceptions += " "
        else:
            slot = text[:text.find(" ")].strip()
            what = text[text.find(" ")+1:]

        s_aux = slot[:]
        for c in charExceptions:
            s_aux = s_aux.replace(c,"")


        if noTags and (" " in slot or len(slot) > maxSlotLen or not s_aux.isalpha()):
            self.bot.sendMessage(chat_id, "The slot can only be one word consisting of 15 alphabetic characters or less.")
        else:
            if not noTags and (len(slot) > maxSlotLen or not s_aux.isalpha()):
                self.bot.sendMessage(chat_id, "The slot inside tags can consist at most of 15 alphabetic characters or less.")
            else:
                w_aux = what[:]
                for c in "'+-1234567890":
                    w_aux = w_aux.replace(c,"")

                if not w_aux.replace(" ", "").isalpha():
                    self.bot.sendMessage(chat_id, "Use only alphabetic characters for the item (or null to delete the slot)")
                else:
                    if len(self.userList[str(msg['from']['id'])]['equipment']) > maxSlots:
                        self.bot.sendMessage(chat_id, "Maximum number of equipment slots in use ("+str(maxSlots)+")")
                    else:
                        if what == "null":
                            try:
                                del self.userList[str(msg['from']['id'])]['equipment'][slot.lower()]
                                update = True
                            except:
                                self.bot.sendMessage(chat_id, "No such slot")
                        else:
                            self.userList[str(msg['from']['id'])]['equipment'][slot.lower()] = what
                            update = True

        return update


    def callback_delequip(self, msg, chat_id):

        update = False
        text = msg['text'][len("/equip"):].strip()

        if "<" not in text and ">" not in text:
            self.bot.sendMessage(chat_id, "Type the name of the slot to delete between tags: <slotname>")
        else:
            slot = text[text.find("<")+len("<") : text.find(">")]

            try:
                del self.userList[str(msg['from']['id'])]['equipment'][slot.lower()]
                update = self.logUsage(self.userList, msg['from'], "/delequip")
            except:
                self.bot.sendMessage(chat_id, "No such slot")

        return update


    def callback_showequip(self, msg, chat_id):

        update = self.logUsage(self.userList, msg['from'], "/showequip")

        equip = ""
        for key in self.userList[str(msg['from']['id'])]['equipment']:
            if self.userList[str(msg['from']['id'])]['equipment'][key] != "":
                equip += key.title() + ": "+ self.userList[str(msg['from']['id'])]['equipment'][key] + "\n"
        if equip != "":
            self.bot.sendMessage(chat_id, equip)
        else:
            self.bot.sendMessage(chat_id, "You are not wearing anything ( ͡° ͜ʖ ͡°)")

        return update


    def callback_cast(self, msg, chat_id):
        update = False
        spell, effect = processSpell(self.spells, msg['from'], msg['text'])

        if spell != "wrong" and effect != "wrong":
            self.bot.sendMessage(chat_id, effect)
            update = self.logUsage(self.userList, msg['from'], spell)

        return update


    # unicode lower case comparison
    def ulower(s1, s2):
        pass


    def usersInGroup(self, group, chat_id):
        users = []
        for key in self.userList:
            if "chats" in self.userList[key]:
                if chat_id in self.userList[key]["chats"]:
                    if "groups" in self.userList[key]:
                        found = (group.lower() == "everyone")
                        i = 0
                        while not found and i < len(self.userList[key]["groups"]):
                            if group.lower() == self.userList[key]["groups"][i].lower():
                                found = True
                            i += 1
                        if found:
                            users.append(key)

                    else:
                        self.userList[key]["groups"] = []

    	return users


    def callback_newjoin(self, msg, chat_id):
        update = self.logUsage(self.userList, msg['from'], "/join")

        group = msg["text"][len("/join "):].strip()

        if group != "":

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:group.find(" ")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:self.MAX_GROUP_NAME_LEN]

            if group == self.strings["no_groups"]:
                self.bot.sendMessage(chat_id, self.strings["that_wont_work"][rand.randint(0, len(self.strings["that_wont_work"])-1)])
            else:

                if "groups" in self.userList[str(msg["from"]["id"])]:
                    if group not in self.userList[str(msg["from"]["id"])]["groups"]:
                        self.userList[str(msg["from"]["id"])]["groups"].append(group)
                else:
                    self.userList[str(msg["from"]["id"])]["groups"] = [group]

        else:
            self.bot.sendMessage(chat_id, self.strings["join_tooltip"])

    	return update


    def callback_newleave(self, msg, chat_id):
        update = self.logUsage(self.userList, msg['from'], "/join")

        group = msg["text"][len("/leave "):].strip()

        if group != "":

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:group.find(" ")]

            if len(group) > self.MAX_GROUP_NAME_LEN:
                group = group[:self.MAX_GROUP_NAME_LEN]


            if "groups" in self.userList[str(msg["from"]["id"])]:
                someLeft = True
                while someLeft:
                    if group in self.userList[str(msg["from"]["id"])]["groups"]:
                        self.userList[str(msg["from"]["id"])]["groups"].remove(group)
                    else:
                        someLeft = False
            else:
                self.userList[str(msg["from"]["id"])]["groups"] = [group]

        else:
            self.bot.sendMessage(chat_id, self.strings["leave_tooltip"])

    	return update


    def callback_newshoutouts(self, msg, chat_id):
        update = self.logUsage(self.userList, msg['from'], "/shoutouts")

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
            for userID in self.usersInGroup(group, chat_id):
                empty = False
                if "username" in self.userList[userID]:
                    message += "@{} ".format(self.userList[userID]["username"], userID)
                else:
                    message += "[{}](tg://user?id={}) ".format(self.userList[userID]["first_name"], userID)

            if empty:
                message = "Empty group"

            self.bot.sendMessage(chat_id, message, parse_mode = "Markdown", reply_to_message_id = msg["message_id"])

        else:
            self.bot.sendMessage(chat_id, self.strings["shoutouts_tooltip"])

        return update


    def callback_lsgroups(self, msg, chat_id):
        update = self.logUsage(self.userList, msg['from'], "/lsgroups")
        if len(self.userList[str(msg["from"]["id"])]["groups"]) > 0:
            self.bot.sendMessage(chat_id, ", ".join(self.userList[str(msg["from"]["id"])]["groups"]))
        else:
            self.bot.sendMessage(chat_id, self.strings["no_groups"])


    # if rand.random() is below comment_threshold, it sends a comment (from strings["comments"])
    # meaning that 1 is always, 0 is never
    def callback_editThresh(self, msg):

        if len(msg['text'].split(" ")[1]) == 3:

            try:
                ret = int(msg['text'].split(" ")[1])
            except:
                ret = self.comment_thresh

        return ret

    def callback_laughAlong(self, chat_id):
        laughs = self.strings["laughs"]
        if (rand.random() < 0.1):
            self.bot.sendMessage(chat_id, laughs[rand.randint(0,len(laughs)-1)])


    def callback_ifc(self, msg, chat_id):
        update = self.logUsage(self.userList, msg['from'], "/ifc")

        dateStr = ""
        txt = msg["text"]
        failed = False

        if txt == "/ifc" or txt == "/ifc@noobdanbot":
            today = dt.date.today()
            self.bot.sendMessage(chat_id, getIFCStringDate(today.day, today.month, today.year))
            return update

        else:
            dateStr = txt[len("/ifc ")+1 : len("/ifc ")+1+10+1].strip()
            if len(dateStr) in [10, 9, 8] and re.match(self.reDict["date"], dateStr):
                try:
                    date = try_parsing_date(dateStr)
                    self.bot.sendMessage(chat_id, getIFCStringDate(date.day, date.month, date.year))
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
        for subr in re.findall(r"r/([^\s/]+)", txt):
            if len(subr) <= self.subRLen:
                message += "[r/{}](https://reddit.com/r/{}) ".format(subr, subr)

        if message != "":
            self.bot.sendMessage(chat_id, message, parse_mode = "Markdown", disable_web_page_preview = True)

    def callback_gdquote(self, msg, chat_id):
        self.logUsage(self.userList, msg['from'], "/gdquote")
        self.bot.sendMessage(chat_id, get_GDQuote())

    def callback_debatemode(self, msg, chat_id):
        usage_msg = "Usage: /debatemode [on|off]"
        self.logUsage(self.userList, msg['from'], "/debatemode")
        args = msg['text'].split(" ")
        if len(args) != 2:
            self.bot.sendMessage(chat_id, usage_msg)
        else:
            switch = args[1]
            if switch == "on":
                self.debatemode = True
            elif switch == "off":
                self.debatemode = False
            else:
                self.bot.sendMessage(chat_id, usage_msg)


    def process_msg(self, msg, content_type, chat_type, chat_id, date, msg_id):

        trolls = [13363913]
        update = self.preliminary_checks(msg)
        prob = rand.randint(1,self.bingoNUM)
        self.bingo_data[-1] += 1
        isEdit = "edit_date" in msg

        if content_type == "text" and msg['text'][:len("/yamete")] == "/yamete":
            print "Taking a break..."
            self.pauseFlag = True
        elif content_type == "text" and msg['text'][:len("/tsudzukete")] == "/tsudzukete":
            print "Carrying on..."
            self.pauseFlag = False

        if msg['from']["is_bot"]:
            print "I see a bot: username {}, first_name {}".format(msg['from']['username'], msg['from']['first_name'])
        else:
            self.updateUserNames(msg)

        if content_type == 'text' and not self.pauseFlag and not msg['from']['id'] in trolls:

            if msg['text'].startswith("/markdown"):
                self.bot.deleteMessage((chat_id, msg_id))
                self.bot.sendMessage(chat_id, msg['text'][len("/markdown "):], parse_mode="Markdown")

            elif  msg['text'][:len('/markov')] == "/markov":
                update = self.callback_markov(msg, chat_id, msg_id)

            elif msg['text'] in ['/help', '/help@noobdanbot']:
                update = self.callback_help(msg, chat_id)

            elif msg['text'] == "Hello Danbot":
                update = self.callback_greet("Hello", msg, chat_id)

            elif msg['text'] == "Hola Danbot":
                update = self.callback_greet("Hola", msg, chat_id)

            elif msg['text'] == "Greetings Danbot":
                update = self.callback_greet("Greetings", msg, chat_id)

            elif msg['text'][:len('/getahk')] == '/getahk':
                update = self.callback_getahk(msg, chat_id)

            elif msg['text'][:len("/hint")] == "/hint":
                update = self.callback_hint(msg, chat_id)

            elif self.passphrase in msg['text']:
                update = self.callback_passphrase(msg, chat_id)

            elif msg['text'][:len('/spamratio')] == "/spamratio":
                update = self.callback_spamratio(msg, chat_id)

            elif msg['text'][:len('/equip')] == "/equip":
                update = self.callback_equip(msg, chat_id)

            elif msg['text'][:len('/delequip')] == "/delequip":
                update = self.callback_delequip(msg, chat_id)

            elif msg['text'][:len('/showequip')] == "/showequip":
                update = self.callback_showequip(msg, chat_id)

            elif msg['text'][:len('Cast ')].lower() == "cast " or\
                    msg['text'][:len('Sing ')].lower() == "sing " or\
                    msg['text'][:len('Pray for ')].lower() == "pray for ":
                update = self.callback_cast(msg, chat_id)

            # elif msg['text'][:len('changecommentthreshold ')] == 'changecommentthreshold ':
            #     aux = self.callback_editThresh(msg)
            #     if aux != None and aux < 1 and aux > 0:
            #         self.comment_thresh = aux
            #     print("Threshold changed to "+str(self.comment_thresh))

            elif msg['text'].lower() == "danbot":
                self.bot.sendMessage(chat_id, ["What?", "Nani?"][rand.randint(0,1)])
            elif msg['text'].lower() in [u"ダンボト", u"暖ボト"]:
                self.bot.sendMessage(chat_id, "何？")
            elif msg['text'].lower() in [u"お前はもう死んでいる"]:
                self.bot.sendMessage(chat_id, "What a weeb")

            elif msg['text'] in self.strings["laugh_triggers"] and not isEdit and not self.debatemode:
                self.callback_laughAlong(chat_id)

            elif msg['text'].startswith("/join"):
                update = self.callback_newjoin(msg, chat_id)

            elif msg['text'].startswith("/leave"):
                update = self.callback_newleave(msg, chat_id)

            elif msg['text'].startswith("/shoutouts") and not isEdit:
                update = self.callback_newshoutouts(msg, chat_id)

            elif msg['text'].startswith("/everyone") and msg['from']['id'] not in trolls and not isEdit:
                msg["text"] = "/shoutouts <everyone>"
                update = self.callback_shoutouts(msg, chat_id)

            elif msg['text'].startswith("/lsgroups"):
                update = self.callback_lsgroups(msg, chat_id)

            elif msg['text'].lower().startswith("/ifc"): # and msg['from']['id'] not in trolls:
                update = self.callback_ifc(msg, chat_id)

            elif msg['text'].startswith("r/"):
                self.callback_subreddit(msg, chat_id)

            elif msg['text'].lower().startswith("danbot say something") or msg['text'].lower().startswith("say something danbot"):
                aggregate = self.strings["comments"] + self.strings["that_wont_work"]
                self.bot.sendMessage(chat_id, aggregate[rand.randint(0, len(aggregate)-1)])

            elif msg['text'].lower().startswith("/gdquote"):
                self.callback_gdquote(msg, chat_id)

            elif msg['text'].lower().startswith("/debatemode"):
                self.callback_debatemode(msg, chat_id)


        if prob == self.bingoNUM:
            jackpot = self.bingo_data[-1]
            print("BINGO! After "+str(self.bingo_data[-1])+" messages")
            saveBingo('./res/bingo_'+str(self.bingoNUM)+'.txt', self.bingo_data)
            self.bingo_data.append(0)
            # Markov --------------------------------------------------
            # sent = self.bot.sendMessage(chat_id, "/markov@Markov_Bot")
            # self.bot.deleteMessage((chat_id, sent['message_id']))
            # Coins (were Adri Quotes) --------------------------------
            # indx = rand.randint(0,len(self.quotes)-1)
            # self.bot.sendMessage(chat_id, self.quotes[indx])
            update = self.addCoinsToUser(jackpot, msg['from'])
            name = get_callsign(msg['from'])
            self.bot.sendMessage(chat_id, "{} just won the jackpot of {} coins++ !!!".format(name, jackpot).upper())

        if update:
            saveJSON(self.user_path, self.userList)

        if rand.random() < self.comment_thresh and not self.debatemode:
            r = rand.randint(0, len(self.strings["comments"])-1)
            self.bot.sendMessage(chat_id, self.strings["comments"][r])



        saveBingo('./res/bingo_'+str(self.bingoNUM)+'.txt', self.bingo_data)




def main():
    pass


if __name__ == '__main__':
    main()
