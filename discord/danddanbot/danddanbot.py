

import discord
import json
import random
import re
import numpy as np
import datetime as dt



# Reads json from filepath and returns the unadultered read contents
def readJSON(filepath):

    with open(filepath, 'r', encoding='utf8') as f:
        data = json.load(f)

    return data


def RollNdX(N, X):
    
    rolls = []
    for i in range(N):
        rolls += [random.randint(1, X)]
    return rolls


def ParseRollArguments(message):
    msg = message.content
    
    msg.replace(" ", "")
    msg.replace("\n", "")
    msg.replace("\t", "")
    # \(\d{0,2})d(4|6|8|10|12|20)([+-]\d{1,2})??
    match = re.search('(?P<num_rolls>\d{0,2})[dD](?P<dice_size>4|6|8|100|12|20|10)(?P<plus_minus>[+-]\d{1,2})?', message.content)

    if(match):
        if(match.group(0)):
            # print("Rolling...")
            # rolls = np.array([], dtype=int)
            rolls = []

            num_rolls = 1 if not match.group("num_rolls") else int(match.group("num_rolls"))
            dice_size = int(match.group("dice_size"))
            mod = 0 if not match.group("plus_minus") else int(match.group("plus_minus"))
            # print(num_rolls, dice_size, mod)
            return num_rolls, dice_size, mod
    return -1, -1, -1


def ParseWorkArguments(message):
    msg = message.content
    
    msg.replace(" ", "")
    msg.replace("\n", "")
    msg.replace("\t", "")

    match = re.search('(?P<plus_minus>[+-]\d{1,2})', message.content)

    if(match):
        if(match.group(0)):

            mod = 0 if not match.group("plus_minus") else int(match.group("plus_minus"))
            
            return mod
    return "-1"

def GetRoleByName(roles, roleName):

    role = None
    for r in roles:
        # print(roleName, r.name, r.name==roleName)
        if r.name == roleName:
            role = r
            break
    return role


def CommandRoll(message):
    
    num_rolls, dice_size, mod = ParseRollArguments(message)
    
    if num_rolls != -1 and dice_size != -1 and mod != -1:
        rolls = RollNdX(int(num_rolls), dice_size)

        response = "Rolls: `{0}`   Mod: `{1}`   Total: `{2}`".format(rolls, mod, sum(rolls) + mod)
        print(response)

        #response = random.randint(1, 20)
        # await message.channel.send(response)
        return response
    else:
        return "-1"


def CommandGold(message):
    
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


def CommandHelp():
    notes = [
            "Dice sizes:  `4, 6, 8, 10, 12, 20, 100`",
            "Supported classes:  `barbarian, bard, cleric, druid, fighter, monk, paladin, ranger, rogue, sorcerer, warlock, wizard`"
        ]
    commandData = [
            ["!roll <N>d<X>+/-<M>", 
                "roll N X-sided dice with M as modifier"],
            ["!gold <class>", 
                "roll starting gold for class"],
            ["!work +/-<M>", 
                "roll for wages based on ability modifier M"],
            ["!addparty <party_name> DM: <dungeon_master> <member1> <member2> <member3> ... <memberN>", 
                '''Creates a party and adds DM and members to it.\
                If the party already exists, adds members to it.\
                DM is overwritten on re-assignment.\
                Note: mention users, rather than typing their usernames or nicknames'''],
            ["!rmparty <party_name>", 
                "removes a party"]
        ]

    return "\n".join(notes) + "\n\n" + "Commands:\n```"+"\n".join(["  -  ".join(e) for e in commandData])+"```"


def CommandWork(message):

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


def CommandAddParty(message):
    
    msg = message.content[len("!addparty "):]
    
    members = []
    roleAndMembers = {}

    dm = None
    dm_name= ""
    # print(message.clean_content)
    for m in message.mentions:
        text = "DM: @" + m.name
        # print(text)
        if (text in message.clean_content):
            if not dm:
                dm_name = m.name
                dm = m
            else:
                return None

    if not dm:
        return None
    else:

        for m in message.mentions:
            if m.name != dm_name:
                members.append(m)
        party_name = msg.split(" ")[0]

        roleAndMembers["party_name"] = party_name
        roleAndMembers["DM"] = dm
        roleAndMembers["members"] = members
        print("NEW PARTY!", roleAndMembers)
        return roleAndMembers


def runBot(filename):
    
    token = ""
    data = readJSON(filename)
    if(data):
        token = data["TOKEN"]
    else:
        return "Problem with the token data file"
    
    logChannelsDict = data["log_channels"]

    client = discord.Client()
    random.seed()

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    @client.event
    async def on_message(message):
        # print(message.content, message.author, client.user)
        if message.author == client.user:
            return

        msg = message.content
        response = "-1"
        if msg.startswith('!roll'):
            response = CommandRoll(message)
        elif msg.startswith('!gold'):
            response = CommandGold(message)
        elif msg.startswith('!help'):
            response = CommandHelp()
        elif msg.startswith('!work'):
            response = CommandWork(message)
        elif msg.startswith("!addparty"):
            roleAndMembers = CommandAddParty(message)
            if not roleAndMembers:
                await message.channel.send("Incorrect format. Check `!help` for more information")
            else:
                role = GetRoleByName(message.guild.roles, roleAndMembers["party_name"])

                today = dt.datetime.today()
                date = dt.date(today.year, today.month, today.day).isoformat()

                header = ""
                newGroup = False

                # if roleAndMembers["party_name"] not in message.guild.roles:
                if not role:
                    role = await message.guild.create_role(name = roleAndMembers["party_name"], mentionable = True)
                    header = "{0} created!".format(roleAndMembers["party_name"])
                    newGroup = True
                else:
                    header = "{0} joined {1}!".format(", ".join([m.name for m in roleAndMembers["members"] if role not in m.roles]), role.name)

                joined = []
                for m in roleAndMembers["members"] + [roleAndMembers["DM"]]:
                    if role not in m.roles:
                        await m.add_roles(role)
                        joined.append(m.name)
                        
                if not newGroup and len(joined) < 1:
                    await message.channel.send("All members are already in the party")
                else:
                    log = "`{date}:` {header} \n`        DM:` {DM}\n`   Members:` {members_string}".format(date = date, header = header, DM = roleAndMembers["DM"].name, members_string = ", ".join([m.name for m in roleAndMembers["members"]]))
                    # print and LOG IT if there's a party log channel

                    if str(message.guild.id) in logChannelsDict:
                        channel_id = logChannelsDict[str(message.guild.id)]
                        await message.guild.get_channel(channel_id).send(log)
                    else:
                        await message.channel.send(log)
                        
                            
        elif msg.startswith("!rmparty"):
            msg = message.content[len("!rmparty "):]
            role = GetRoleByName(message.guild.roles, msg)
            if not role:
                await message.channel.send("Role not found.".format(role = role))
            else:
                # await message.guild.delete_role(role)
                await role.delete()
                header = "Role \"{role}\" deleted.".format(role = role)
                                
                today = dt.datetime.today()
                date = dt.date(today.year, today.month, today.day).isoformat()

                log = "`{date}:` {header}".format(date = date, header = header)

                # print and LOG IT if there's a party log channel
                if str(message.guild.id) in logChannelsDict:
                    channel_id = logChannelsDict[str(message.guild.id)]
                    await message.guild.get_channel(channel_id).send(log)
                else:
                    await message.channel.send(log)

        elif msg.startswith("QQ"):
            dm = ""
            for m in message.mentions:
                text = "DM @" + m.name
                if (text in message.clean_content):
                    dm = m.name
            await message.channel.send("```DM is @"+str(dm)+"```")
            # else:
                # await message.channel.send(" ".join([text, "|in|", msg]))
                # for c in (msg):
                #     await message.channel.send(str(c))
                # await message.channel.send(message.clean_content)

        if response != "-1":
            await message.channel.send(response)


    client.run(token)

    return "Session ended."


def main():
    exitCode = runBot('config.json')


if __name__ == "__main__":
    main()