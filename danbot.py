# -*- coding: utf-8 -*-

import random as rand

from processSpells import *
from dbHandler import *
from getAHK import *



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
        # print userList.keys()
    except:
        ret =  msg_from['first_name']
        # print userList.keys()
    return ret

def get_name(msg_from):

    try:
        ret = msg_from['first_name']
        # print userList.keys()
    except:
        ret =  msg_from['username']
        # print userList.keys()
    return ret


class DanBot(object):

    def __init__(self):

        self.strings = readJSON("./res/strings/en-Uk/strings.json")
        self.quotes = getQuotes('./res/Quotes.txt')

        self.bingoNUM = 512
        self.bingo_data = readBingo('./res/bingo_'+str(self.bingoNUM)+'.txt')

        self.passphrase = self.strings["passphrase"]
        self.default_passphrase = self.strings["default_passphrase"]

        self.user_path = "./res/users.json"
        self.userList = readJSON(self.user_path)

        self.spell_path = './res/strings/en-Uk/spells.json'
        self.spells = readJSON(self.spell_path)
        self.pauseFlag = False

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
            self.newUser(msg)
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


    def logUsage(self, userList, user, command):
        userid = str(user['id'])
        if command in self.userList[userid]['cmdUsage']:
            self.userList[userid]['cmdUsage'][command] = str(1+int(self.userList[userid]['cmdUsage'][command]))
        else:
            self.userList[userid]['cmdUsage'][command] = "1"

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
            self.bot.sendMessage(chat_id, txt + " " + get_name(msg['from'] + ".\nI am the new Danbot"))

        return update

    def callback_getahk(self, msg):

        update = self.logUsage(self.userList, msg['from'], "/getahk")

        if "/getahk@noobdanbot" in msg['text']:
            st = len("/getahk@noobdanbot ")
        else:
            st = len("/getahk ")

        cod = msg['text'][st+1-1:-1]
        frame = "on"

        if msg['text'][len("/getahk")] == "!":
            frame = "off"

        try:
            ahk = getAHK(cod, frame)
            self.bot.sendMessage(chat_id, "AHK code to paste in hotkey:\n```"+ahk+"```", parse_mode = "Markdown")
        except:
            self.bot.sendMessage(chat_id, "Error getting AHK code.")

        return update

    def callback_hint(self, msg):

        update = self.logUsage(self.userList, msg['from'], "/hint")
        self.bot.sendMessage(chat_id, self.strings["hint"])
        return update

    def callback_passphrase(self, msg):

        update = self.logUsage(self.userList, msg['from'], "Passphrase")

        indx = rand.randint(0,len(self.quotes)-1)
        self.bot.sendMessage(chat_id, self.quotes[indx])

        if self.passphrase == "I'm a Fusion":
            self.passphrase = str(rand.randint(0,999999999))
        else:
            self.passphrase = "I'm a Fusion!"


    def callback_spamratio(self, msg):

        if (msg['text'] == "/spamratio" or msg['text'] == "/spamratio@noobdanbot"):

            bot.sendMessage(chat_id, self.strings["spamratio_tooltip"])

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
            bot.sendMessage(chat_id, ret)

            return update


    def callback_equip(self, msg):

        update = self.logUsage(self.userList, msg['from'], "/equip")

        maxSlotLen = 15
        maxSlots = 16
        noTags = True
        charExceptions = "+-1234567890"

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
            bot.sendMessage(chat_id, "The slot can only be one word consisting of 15 alphabetic characters or less.")
        else:
            if not noTags and (len(slot) > maxSlotLen or not s_aux.isalpha()):
                bot.sendMessage(chat_id, "The slot inside tags can consist at most of 15 alphabetic characters or less.")
            else:
                w_aux = what[:]
                for c in "'+-1234567890":
                    w_aux = w_aux.replace(c,"")

                if not w_aux.replace(" ", "").isalpha():
                    bot.sendMessage(chat_id, "Use only alphabetic characters for the item (or null to delete the slot)")
                else:
                    if len(userList[str(msg['from']['id'])]['equipment']) > maxSlots:
                        bot.sendMessage(chat_id, "Maximum number of equipment slots in use ("+str(maxSlots)+")")
                    else:
                        if what == "null":
                            try:
                                del userList[str(msg['from']['id'])]['equipment'][slot.lower()]
                                update = True
                            except:
                                bot.sendMessage(chat_id, "No such slot")
                        else:
                            userList[str(msg['from']['id'])]['equipment'][slot.lower()] = what
                            update = True

        return update


    def callback_delequip(self, msg):

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


    def callback_showequip(self, msg):

        update = self.logUsage(userList, msg['from'], "/showequip")

        equip = ""
        for key in self.userList[str(msg['from']['id'])]['equipment']:
            if self.userList[str(msg['from']['id'])]['equipment'][key] != "":
                equip += key.title() + ": "+ self.userList[str(msg['from']['id'])]['equipment'][key] + "\n"
        if equip != "":
            self.bot.sendMessage(chat_id, equip)
        else:
            self.bot.sendMessage(chat_id, "You are not wearing anything ( ͡° ͜ʖ ͡°)")

        return update


    def callback_cast(self, msg):

        spell, effect = processSpell(spells, msg['from'], msg['text'])

        if spell != "wrong" and effect != "wrong":
            self.bot.sendMessage(chat_id, effect)
            update = self.logUsage(self.userList, msg['from'], spell)

        return update




    def process_msg(self, msg, content_type, chat_type, chat_id, date, msg_id):

        update = self.preliminary_checks(msg)

        prob = rand.randint(1,self.bingoNUM)
        self.bingo_data[-1] += 1

        if content_type == "text" and msg['text'][:len("/yamete")] == "/yamete":
            print "Taking a break..."
            self.pauseFlag = True
        elif content_type == "text" and msg['text'][:len("/tsudzukete")] == "/tsudzukete":
            print "Carrying on..."
            self.pauseFlag = False


        if content_type == 'text' and not self.pauseFlag:

            if  msg['text'][:len('/markov')] == "/markov":
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
                update = self.callback_getahk(msg)

            elif msg['text'][:len("/hint")] == "/hint":
                update = self.callback_hint(msg)

            elif self.passphrase in msg['text']:
                update = self.callback_passphrase(msg)

            elif msg['text'][:len('/spamratio')] == "/spamratio":
                update = self.callback_spamratio(msg)

            elif msg['text'][:len('/equip')] == "/equip":
                update = self.callback_equip(msg)

            elif msg['text'][:len('/delequip')] == "/delequip":
                update = self.callback_delequip(msg)

            elif msg['text'][:len('/showequip')] == "/showequip":
                update = self.callback_showequip(msg)

            elif msg['text'][:len('Cast ')] == "Cast " or\
                    msg['text'][:len('Sing ')] == "Sing " or\
                    msg['text'][:len('Pray for ')] == "Pray for ":
                update = self.callback_cast(msg)


        if update:
            saveJSON(self.user_path, self.userList)

        if prob == self.bingoNUM:
            print("BINGO! After "+str(self.bingo_data[-1])+" messages")
            saveBingo('bingo_'+str(self.bingoNUM)+'.txt', self.bingo_data)
            self.bingo_data.append(0)
            # Markov --------------------------------------------------
            # sent = self.bot.sendMessage(chat_id, "/markov@Markov_Bot")
            # self.bot.deleteMessage((chat_id, sent['message_id']))
            # Adri Quotes ---------------------------------------------
            indx = rand.randint(0,len(self.quotes)-1)
            bot.sendMessage(chat_id, self.quotes[indx])


        saveBingo('bingo_'+str(self.bingoNUM)+'.txt', self.bingo_data)



def main():
    pass


if __name__ == '__main__':
    main()
