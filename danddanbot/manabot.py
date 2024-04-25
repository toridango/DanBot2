import discord
import random
import json
import regex as re
from dyce import H, P
from dyce.evaluation import expandable


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

def ParseRollArguments2(message):
    msg = message.content
    
    msg = msg.replace(" ", "")
    msg = msg.replace("\n", "")
    msg = msg.replace("\t", "")

    rolls = []
    total_mod = 0

    # pattern = r"((?P<num>[+\-]?\d{0,3})[dD](?P<dice_size>\d{1,3}))|(?P<mod>[+\-]\d{1,3})|(?P<select>kh|kl)|((?P<compare>lt|le|gt|ge)(?P<comparison>\d{1,2}))"
    pattern = r"((?P<num>[+\-]?\d{0,3})[dD](?P<dice_size>\d{1,3})(?P<select>kh|kl)?)|(?P<mod>[+\-]\d{1,3})"
    for m in re.finditer(pattern, msg):
        num = m.group("num")
        dice_size = m.group("dice_size")
        select = m.group("select")
        mod = m.group("mod")

        if dice_size:
            n = 1 if not num else int(num) if num not in "+-" else int(num+"1")
            if select:
                rolls += [(n, int(dice_size), select)]
                # if not last_roll[-1]: # if the selector in the last roll is not set
            else:
                rolls += [(n, int(dice_size), None)]
        elif mod:
            total_mod += int(mod)

    return rolls, total_mod

def ParseHistogramArguments(message):
    msg = message.content
    
    msg = msg.replace(" ", "")
    msg = msg.replace("\n", "")
    msg = msg.replace("\t", "")

    rolls = []
    total_mod = 0
    sel = ""
    comp = []

    # pattern = r"((?P<num>[+\-]?\d{0,3})[dD](?P<dice_size>\d{1,3}))|(?P<mod>[+\-]\d{1,3})|(?P<select>kh|kl)|((?P<compare>lt|le|gt|ge)(?P<comparison>\d{1,2}))"
    pattern = r"((?P<num>[+\-]?\d{0,3})[dD](?P<dice_size>\d{1,3})(?P<select>kh|kl)?)|(?P<mod>[+\-]\d{1,3})|((?P<compare>lt|le|gt|ge)(?P<comparison>\d{1,2}))"
    for m in re.finditer(pattern, msg):
        num = m.group("num")
        dice_size = m.group("dice_size")
        select = m.group("select")
        mod = m.group("mod")
        compare = m.group("compare")
        comparison = m.group("comparison")

        if dice_size:
            n = 1 if not num else int(num) if num not in "+-" else int(num+"1")
            if select:
                rolls += [(n, int(dice_size), select)]
                # if not last_roll[-1]: # if the selector in the last roll is not set
            else:
                rolls += [(n, int(dice_size), None)]
        elif mod:
            total_mod += int(mod)
        elif compare and comparison:
            if not comp: # if still not set
                comp = [compare, int(comparison)]

    return rolls, total_mod, comp

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

MAX_REC = 10
def reroll_ones_recursive(h, limit = None):

    @expandable(sentinel=h)
    def reroll_ones(h_result):
        if h_result.outcome == 1:
            return reroll_ones(h_result.h)
        else:
            return h_result.outcome
    return reroll_ones(h, limit=limit)

def HistogramStats(reroll=10):
    # reroll 0 never, 1 once, >=10 always 
    if reroll == 0:    
        p_4d6 = 4@P(6)
        return p_4d6.h(slice(1, None)) # drop lowest
    elif reroll > 0 and reroll < 10:        
        p_4d6_reroll_first_one = 4@P(reroll_ones_recursive(H(6), 1))
        return p_4d6_reroll_first_one.h(slice(1, None)) # drop lowest
    elif reroll >= 10:
        p_4d6_reroll_all_ones = 4 @ P(H(5) + 1)
        return p_4d6_reroll_all_ones.h(slice(1, None)) # drop lowest
    return None

class ManaClient(discord.Client):
    async def on_ready(self):
        print(f'Mana is flowing as {self.user}!')

    async def on_message(self, message):
        # print(f'Message from {message.author}: {message.content}')
        
        if message.author == self.user:
            return

        msg = message.content.lower()
        response = "-1"
        if msg.startswith('!'):
            print(f'Message from {message.author}: {message.content}')

            if msg.startswith('!help'):
                response = self.command_help(message)
            elif msg.startswith('!roll'):
                response = self.command_roll(message)
            elif msg.startswith('!r'):
                response = self.command_r(message)
            elif msg.startswith('!gold'):
                response = self.command_gold(message)
            elif msg.startswith('!work'):
                response = self.command_work(message)
            elif msg.startswith("!stats"):
                response = self.command_stats(message)
            elif msg.startswith("!s"):
                response = self.command_s(message)
            elif msg.startswith("!h"):
                response = self.command_h(message)

        if response != "-1":
            await message.channel.send(response)

    def command_help(self, message):
        command_data = [
                ["!roll <N>d<X> [+/-<M>]", 
                    "roll `N` `X`-sided dice with `M` as an optional modifier.\ne.g. `!roll d20`, `!roll 2d6`, `!roll 1d20+5`"],
                ["!r <N>d<X>[kh|kl] [+ <M>]", 
                    "roll 1 or more sets of dice (`N` `X`-sided dice) with `kh` and `kl` as optional selectors (keep highest and keep lowest) and `M` as an optional modifier.\ne.g. `!r d20+4`, `!r 2d6`, `!r 2d20kh+5`.\nThis command rolls using the same framework as the probability command."],
                ["!gold <class>", 
                    "roll starting gold for class\nSupported classes:  `barbarian, bard, cleric, druid, fighter, monk, paladin, ranger, rogue, sorcerer, warlock, wizard`.\ne.g. `!gold monk`."],
                ["!stats <N>", 
                    "rolls `N` stats (never rerolls ones), or 6 if unspecified.\ne.g.`!stats`, `!stats 1`"],
                ["!s [rr0|rr1]", 
                    "rolls 6 stats (rerolls all ones unless rr0 or rr1 is specified). With rr0 or rr1 as optional flags, the maximum amount of rerolls is specified as 1 (the first one you get) or 0 (never reroll).\ne.g. `!s`, `!s rr0`."],
                ["!h <N>d<X>[kh|kl] [+ M] [lt|le|gt|ge <C>]", 
                    "displays probability distribution of `N` rolls of `X`-sided dice, with `M` as an optional modifier.\ne.g. `!h d20`, `!h 2d6klge2`, `!h 2d20kh+5-1d4+1d8ge20`.\nOptional selectors (can be specified for each dice set): `kh` (keep highest), `kl` (keep lowest).\nOptional comparison `lt` (less than), `le` (less or equal), `gt` (greater than), or `ge` (greater or equal) to <C>.\nSpecial option: `!h stats [rr0|rr1]` :will display distribution for 4d6 drop lowest. Always rerolls ones by default (add `rr0` for no rerolls, `rr1` for reroll first one)"]
            ]
        msg = message.content
        if msg != "!help":
            if "roll" in msg:
                c = command_data[0]
                return "Command `roll`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
            elif "gold" in msg:
                c = command_data[2]
                return "Command `gold`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
            elif "stats" in msg:
                c = command_data[3]
                return "Command `stats`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
            elif "r" in msg:
                c = command_data[1]
                return "Command `r`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
            elif "s" in msg:
                c = command_data[4]
                return "Command `s`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
            elif "h" in msg:
                c = command_data[5]
                return "Command `h`:\n"+"`{0}`    {1}\n".format(c[0], c[1])
        return "Commands:\n"+"\n".join(["`{0}`    {1}\n".format(e[0], e[1]) for e in command_data]) #+ "\n\n" + "\n".join(notes)

    def command_roll(self, message):    
        num_rolls, dice_size, mod = ParseRollArguments(message)
        
        if num_rolls != -1 and dice_size != -1 and mod != -1:
            rolls = RollNdX(num_rolls, dice_size)

            response = "Rolls: `{0}`   Mod: `{1}`   Total: `{2}`".format(rolls, mod, sum(rolls) + mod)
            print(response)

            return response
        else:
            return "-1"
        
    def command_r(self, message):    
        rolls, mod = ParseRollArguments2(message)

        trans_to_int = {"kh":-1, "kl":0} # translation dict
        total = 0
        str_results = []
        
        # print(rolls, mod, comparison)
        if rolls:
            # pools = []
            for n, x, s in rolls:
                if n == 0:
                    continue

                pool = abs(n)@P(x) if abs(n) > 1 else H(x)
                r = pool.roll()
                if not s:
                    if type(r) is int:
                        total = total + r if n > 0 else total - r
                        # str_results += ["`+{}`".format(r) if n > 0 else "`-{}`".format(r)]
                    else:
                        total = total + sum(r) if n > 0 else total - sum(r)
                    str_results += ["`+{}`".format(r) if n > 0 else "`-{}`".format(r)]

                else:
                    res = 0
                    if s == "kh":
                        res = max(r)
                    elif s == "kl":
                        res = min(r)
                    total = total + res if n > 0 else total - res
                    str_results += ["`+{}` from `{}`".format(res, r) if n > 0 else "`-{}` from `{}`".format(res, r)]

            if mod:
                total += mod

            return "Rolls: {}\n(Mod: `{:+}`)\nTOTAL: `{}`".format("["+", ".join(str_results)+"]", mod, total)
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
        match = re.search("(?P<num_stats>\d{1,2})", msg)
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

    def command_s(self, message, num_stats=6):        
        msg = message.content
        response = ""
        total_point_buy = 0
        
        for i in range(num_stats):
            roll = ()
            if "rr0" in msg:    
                p_4d6 = 4@P(6)
                roll = p_4d6.roll()
            elif "rr1" in msg:        
                p_4d6_reroll_first_one = 4@P(reroll_ones_recursive(H(6), 1))
                roll = p_4d6_reroll_first_one.roll()
            else: # reroll always
                p_4d6_reroll_all_ones = 4 @ P(H(5) + 1)
                roll = p_4d6_reroll_all_ones.roll()            
                        
            sorted_roll = sorted(roll, reverse=True)
            stat = sum(sorted_roll[0:-1])
            point_buy = stat - 8 if stat < 14 else (stat - 8) + (stat - 13) 
            total_point_buy += point_buy
            response += "`{4:2} = `({0} + {1} + {2} + ~~{3}~~)\n".format(*sorted_roll, stat)
            
        response += "Total point buy cost: {0}".format(total_point_buy)
        return response

    def handle_command_h_stats(self, message):        
        if "rr0" in message.content:
            h = HistogramStats(0)
            response = "Histogram for 4d6 (drop lowest, no rerolls)\n```{}```".format(h.format())
            return response
        elif "rr1"in message.content:
            h = HistogramStats(1)
            response = "Histogram for 4d6 (drop lowest, reroll first one)\n```{}```".format(h.format())
            return response
        else:
            h = HistogramStats()
            response = "Histogram for 4d6 (drop lowest, always reroll)\n```{}```".format(h.format())
            return response

    def command_h(self, message):    
        if message.content.startswith("!h stats"):
            return self.handle_command_h_stats(message)

        # (([+\-]?\d{0,3})[dD](\d{1,3})(kh|kl)?)|([+\-]\d{1,3})|((lt|le|gt|ge)(\d{1,2}))
        rolls, mod, comparison = ParseHistogramArguments(message)
        trans_to_int = {"kh":-1, "kl":0} # translation dict
        trans_to_str = {"kh":" (keep highest)", "kl":" (keep lowest)", None: ""} # translation dict
        str_select = ""
        str_compare = ""
        
        # print(rolls, mod, comparison)
        if rolls:
            pools = []
            for n, x, s in rolls:
                pool = n@P(x) if n>0 else abs(n)*-P(x)
                if not s:
                    pools += [pool]
                elif s in trans_to_int.keys():
                    pools += [pool.h(trans_to_int[s])]
                    
            h = sum(pools)

            if mod:
                h += mod

            if comparison:
                compare = comparison[0]
                to = comparison[1]
                if "lt" in compare:
                    h = P(h).lt(to)
                    str_compare += " is less than {}".format(to)
                elif "le" in compare:
                    h = P(h).le(to)
                    str_compare += " is less or equal to {}".format(to)
                elif "gt" in compare:
                    h = P(h).gt(to)
                    str_compare += " is greater than {}".format(to)
                elif "ge" in compare:
                    h = P(h).ge(to)
                    str_compare += " is greater or equal to {}".format(to)

            str_rolls = "".join([" {:+}d{}{}".format(n,x,trans_to_str[s]) for n,x,s in rolls])
            response = "Histogram for {0} {1:+}{2}{3}\n```{4}```".format(str_rolls, mod, str_select, str_compare, h.format())
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