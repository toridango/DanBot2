

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

def getID_and_callsign():

    ret = str(msg['from']['id']) + ": "

    try:
        ret += msg['from']['username']
        # print userList.keys()
    except:
        ret +=  msg['from']['first_name']
        # print userList.keys()

    return ret


class DanBot(object):


    def __init__(self):

        self.strings = readJson(keysPath)

        self.bote = 0
        self.bingoNUM = 512
        self.passphrase = self.strings["passphrase"]
        self.default_passphrase = self.strings["default_passphrase"]
        self.firstMsg = True
        self.userList = {}
        self.users = {}
        self.spells = {}
        self.pauseFlag = False


    def process_msg(self, msg, content_type, chat_type, chat_id, date, msg_id):

        update = False

        if 'left_chat_member' in msg.keys():
            print "MEMBER LEFT"

        if str(msg['from']['id']) not in userList.keys():

            print(getID_and_callsign(msg))
            userList[str(msg['from']['id'])] = msg['from']
            userList[str(msg['from']['id'])]['id'] = str(userList[str(msg['from']['id'])]['id'])
            userList[str(msg['from']['id'])]["equipment"] = {}
            userList[str(msg['from']['id'])]["titles"] = []
            userList[str(msg['from']['id'])]["cmdUsage"] = []
            update = True



        if update:
            with open('users.json','w') as outfile:
                json.dump(userList, outfile)
