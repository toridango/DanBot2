import discord
import random
import json
import regex as re
from dyce import H, P

# d4 = H(4)
# d6 = H(6)
# d8 = H(8)
# d10 = H(10)-1
# d12 = H(12)
# d20 = H(20)
# d100 = H(100)

# Reads json from filepath and returns the unadultered read contents
def readJSON(filepath):

    with open(filepath, "r", encoding="utf8") as f:
        data = json.load(f)

    return data

def RollNdX(N, X):
    
    rolls = []
    for i in range(N):
        rolls += [random.randint(1, X)]
    return rolls

def ParseRollArguments(message):
    msg = message.content#[len("!roll "):]
    
    msg = msg.replace(" ", "")
    msg = msg.replace("\n", "")
    msg = msg.replace("\t", "")
    # \(\d{0,2})d(4|6|8|10|12|20)([+-]\d{1,2})??
    # print(msg)
    # match = re.search("(?P<num_rolls>\d{0,2})[dD](?P<dice_size>4|6|8|100|12|20|10)(?P<plus_minus>[+-]\d{1,2})?", msg)
    match = re.search("(?P<num_rolls>\d{0,2})[dD](?P<dice_size>100|\d{1,2})(?P<plus_minus>[+-]\d{1,2})?", msg)

    if(match):
        if(match.group(0)):
            # print("Rolling...")
            # rolls = np.array([], dtype=int)
            rolls = []

            num_rolls = 1 if not match.group("num_rolls") else int(match.group("num_rolls"))
            dice_size = int(match.group("dice_size"))
            mod = 0 if not match.group("plus_minus") else int(match.group("plus_minus"))
            # print(num_rolls, dice_size, mod)
            if(dice_size > 0):
                return num_rolls, dice_size, mod
    return -1, -1, -1

def ParseHistogramArguments(message):
    msg = message.content#[len("!roll "):]
    
    msg = msg.replace(" ", "")
    msg = msg.replace("\n", "")
    msg = msg.replace("\t", "")
    match = re.search("(?P<num_rolls>\d{0,2})[dD](?P<dice_size>100|\d{1,2})(?P<plus_minus>[+-]\d{1,2})?(?P<select>kh|kl)?((?P<compare>lt|le|gt|ge)(?P<comparison>\d{1,2}))?", msg)
    if(match):
        if(match.group(0)):
            # rolls = np.array([], dtype=int)
            rolls = []

            num_rolls = 1 if not match.group("num_rolls") else int(match.group("num_rolls"))
            dice_size = int(match.group("dice_size"))
            mod = 0 if not match.group("plus_minus") else int(match.group("plus_minus"))
            select = "" if not match.group("select") else match.group("select")
            compare = "" if not match.group("compare") else match.group("compare")
            comparison = 0 if not match.group("comparison") else int(match.group("comparison"))
            # print(num_rolls, dice_size, mod)
            if(dice_size > 0):
                return num_rolls, dice_size, mod, select, compare, comparison
    return -1, -1, -1, "", "", 0

def ParseWorkArguments(message):
    msg = message.content
    
    msg = msg.replace(" ", "")
    msg = msg.replace("\n", "")
    msg = msg.replace("\t", "")

    match = re.search("(?P<plus_minus>[+-]\d{1,2})", msg)

    if(match):
        if(match.group(0)):

            mod = 0 if not match.group("plus_minus") else int(match.group("plus_minus"))
            
            return mod
    return "-1"

class ManaClient(discord.Client):
    async def on_ready(self):
        print(f'Mana is flowing as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        
        if message.author == self.user:
            return

        msg = message.content
        response = "-1"
        if msg.startswith('!'):
            if msg.startswith('!help'):
                response = self.command_help(message)
            elif msg.startswith('!roll'):
                response = self.command_roll(message)
            elif msg.startswith('!gold'):
                response = self.command_gold(message)
            elif msg.startswith('!work'):
                response = self.command_work(message)
            elif msg.startswith("!stats"):
                response = self.command_stats(message)
            elif msg.startswith("!H"):
                response = self.command_histogram(message)

        if response != "-1":
            await message.channel.send(response)

    def command_help(self, message):
        command_data = [
                ["!roll <N>d<X>+/-<M>", 
                    "roll N X-sided dice with M as an optional modifier"],
                ["!gold <class>", 
                    "roll starting gold for class\nSupported classes:  `barbarian, bard, cleric, druid, fighter, monk, paladin, ranger, rogue, sorcerer, warlock, wizard`"],
                ["!work +/-<M>", 
                    "roll for wages based on ability modifier M"],
                ["!stats <N>", 
                    "rolls N stats, or 6 if unspecified"],
                ["!histogram <N>d<X> [+ M] [kh|kl] [lt|le|gt|ge <C>] ", 
                    "displays probability distribution of N rolls of X-sided dice, with M as an optional modifier\nOptional selectors: kh (keep highest), kl (keep lowest)\nOptional comparison lt (less than), le (less or equal), gt (greater than), or ge (greater or equal) to <C>"]
            ]
        return "Commands:\n"+"\n".join(["`{0}`    {1}\n".format(e[0], e[1]) for e in command_data])

    def command_roll(self, message):    
        num_rolls, dice_size, mod = ParseRollArguments(message)
        
        if num_rolls != -1 and dice_size != -1 and mod != -1:
            rolls = RollNdX(num_rolls, dice_size)

            response = "Rolls: `{0}`   Mod: `{1}`   Total: `{2}`".format(rolls, mod, sum(rolls) + mod)
            print(response)

            #response = random.randint(1, 20)
            # await message.channel.send(response)
            return response
        else:
            return "-1"
        
    def command_gold(self, message):
    
        msg = message.content
        response = "-1"
        classStr = msg[len("!gold "):].lower()

        # dict with: class: (num_rolls, dice_size, gold_multiplier)
        classDict = {
            "barbarian":    (2, 4, 10),
            "bard":         (5, 4, 10),
            "cleric":       (5, 4, 10),
            "druid":        (2, 4, 10),
            "fighter":      (5, 4, 10),
            "monk":         (5, 4,  1),
            "paladin":      (5, 4, 10),
            "ranger":       (5, 4, 10),
            "rogue":        (4, 4, 10),
            "sorcerer":     (3, 4, 10),
            "warlock":      (4, 4, 10),
            "wizard":       (4, 4, 10)
        }

        if classStr not in classDict:
            response = "Class not recognised"
        else:
            values = classDict[classStr]
            rolls = RollNdX(values[0], values[1])
            response = "{0} starting gold: `{1}d{2}·{3}`\nRolls: `{4}`   Starting gold: `{5}`gp".format(classStr.capitalize(), values[0], values[1], values[2], rolls, sum(rolls) * values[2])

        return response
    
    def command_work(self, message):
        mod = ParseWorkArguments(message)
        rolls = []
        response = "-1"

        if not isinstance(mod, str):        
            rolls = RollNdX(1, 20)
            rollTotal = sum(rolls) + mod
            
            wages = 0

            if rollTotal >= 21:
                wages = 55
            elif rollTotal >= 15:
                wages = 20
            elif rollTotal >= 10:
                wages = 10
            else:
                wages = 2

            response = "You earn: `{0}` gold pieces".format(wages)

            

        return response


    def command_stats(self, message):        
        msg = message.content
        response = ""
        match = re.search("(?P<num_stats>\d{0,2})", msg)
        num_stats = 6 if not match.group("num_stats") else int(match.group("num_stats"))
        if num_stats < 1:
            num_stats = 6

        stats = []
        rollGroups = []
        discardedIndices = []

        totalPointBuyValue = 0

        for i in range(num_stats):
            roll = RollNdX(4, 6)
            stat = sum(roll) - min(roll)

            stats.append(stat)
            rollGroups.append(roll)

            pointBuyValue = stat - 8 if stat < 14 else (stat - 8) + (stat - 13) 
            totalPointBuyValue += pointBuyValue

            sortedRoll = sorted(roll, reverse=True)
            response += "`{4:2} = `({0} + {1} + {2} + ~~{3}~~)\n".format(*sortedRoll, stat)
            
        response += "Total point buy cost: {0}".format(totalPointBuyValue)


        return response
    
    def command_histogram(self, message):    
        num_rolls, dice_size, mod, select, compare, comparison = ParseHistogramArguments(message)
        
        if num_rolls != -1 and dice_size != -1 and mod != -1:
            # dS = H(dice_size)
            pNdS = num_rolls@P(dice_size)

            str_select = ""
            str_compare = ""
            if select != "":
                if "kh" in select:
                    h = P(pNdS).h(-1)
                    str_select = " keep highest"
                elif "kl" in select:
                    h = P(pNdS).h(0)
                    str_select = " keep lowest"

                if compare != "":
                    str_compare += ", then check if"
            else:            
                h = pNdS.h()

            h = h+mod

            if compare != "":
                if "lt" in compare:
                    h = P(h).lt(comparison)
                    str_compare += " is less than {}".format(comparison)
                elif "le" in compare:
                    h = P(h).le(comparison)
                    str_compare += " is less than or equal to {}".format(comparison)
                elif "gt" in compare:
                    h = P(h).gt(comparison)
                    str_compare += " is greater than {}".format(comparison)
                elif "ge" in compare:
                    h = P(h).ge(comparison)
                    str_compare += " is greater than or equal to {}".format(comparison)

            response = "Histogram for {0}d{1}{2:+}{3}{4}\n```{5}```".format(num_rolls, dice_size, mod, str_select, str_compare, h.format())
            # print(response)

            return response
        else:
            return "-1"



def runBot(filename):
    random.seed()
    
    data = readJSON(filename)
    if not data:
        return "Problem with the token data file"
    
    token = data["MANABOT_TOKEN"]

    intents = discord.Intents.default()
    intents.message_content = True

    client = ManaClient(intents=intents)
    client.run(token)

    return "No more Mana!"

def main():
    exitCode = runBot("./config.json")
    print(exitCode)

if __name__ == "__main__":
    main()