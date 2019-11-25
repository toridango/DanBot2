# -*- coding: utf-8 -*-
import random as rand


# Reqs: target, cast, sing, pray
def checksReqs(reqs, cf, sf, pf, tf, gf, glyph, verbose=False):
    if verbose:
        print(reqs, "cf", cf, "sf", sf, "pf", pf, "tf", tf, "gf", gf, glyph)
    cf = (("cast" in reqs) == cf) or not ("sing" in reqs or "pray" in reqs)
    sf = (("sing" in reqs) == sf) or not ("cast" in reqs or "pray" in reqs)
    pf = ("pray" in reqs) == pf
    tf = (("target" in reqs) == tf) or not "target" in reqs
    gf = ("glyph "+glyph in reqs) == gf

    return all([cf, sf, pf, tf, gf])

def processSpell(spells, casterDict, text, verbose=False):
    glyph_flag = ("draw" in text.lower() and "glyph" in text.lower())
    cast_flag = "cast" in text.lower()
    sing_flag = "sing" in text.lower()
    spell_flag = "spell" in text.lower()
    pray_flag = "pray for" in text.lower()
    # print "cf",cast_flag,"sf",sing_flag,"pf",pray_flag,"gf",glyph_flag

    glyph = ""
    cast = ""
    sing = ""
    pray = ""
    TRGT = ""
    CSTR = ""

    spell = ""
    effect = ""

    if (cast_flag and sing_flag) or (cast_flag and pray_flag) or (pray_flag and sing_flag) or (spell_flag and pray_flag) or (not cast_flag and not sing_flag and not pray_flag):
        return "wrong", "wrong"


    trgt_flag = False

    if cast_flag and "on " in text:
        trgt_flag = True
        TRGT = text[text.find("on ") + len("on "):]

    elif sing_flag and "to " in text:
        trgt_flag = True
        TRGT = text[text.find("to ") + len("to "):]

    CSTR = casterDict['first_name']

    if verbose:
        print("target", trgt_flag, "||", CSTR, "->", TRGT)

    if glyph_flag:
        glyph = text[text.find("Draw ") + len("Draw ") : text.find(" glyph")]

        if glyph not in spells['glyphs']:
            return "wrong", "wrong"

    spell_lims = ["", ""]

    if trgt_flag:
        if cast_flag:
            spell_lims[1] = " on"
        elif sing_flag:
            spell_lims[1] = " to"

    if spell_flag:
        spell_lims[1] = " spell"

    if cast_flag:
        spell_lims[0] = "cast "
    elif sing_flag:
        spell_lims[0] = "sing "
    elif pray_flag:
        spell_lims[0] = "pray for "


    if spell_lims[1] == "":
        spell = text[text.lower().find(spell_lims[0]) + len(spell_lims[0]) : ].lower()
    else:
        spell = text[text.lower().find(spell_lims[0]) + len(spell_lims[0]) : text.lower().find(spell_lims[1])].lower()

    if verbose:
        print(spell)

    if spell not in spells['spells']:
        if spell not in spells['translations']:
            return "wrong", "wrong"
        else:
            spell = spells['translations'][spell]


    if not checksReqs(spells['spells'][spell]['requires'], cast_flag, sing_flag, pray_flag, trgt_flag, glyph_flag, glyph):
            return "wrong", "wrong"
    else:
        effect = spells['spells'][spell.lower()]['text'][rand.randint(0, len(spells['spells'][spell]['text'])-1)]


    if "CSTR" in effect:
        effect = effect.replace("CSTR", CSTR)

    if "TRGT" in effect:
        if trgt_flag:
            effect = effect.replace("TRGT", TRGT)
        else:
            effect = effect.replace("TRGT", CSTR)

    return spell, effect




if __name__ == '__main__':
    spells = {}
    caster = {"1": {"username": "JDUser", "first_name": "Jane", "last_name": "Doe", "id": "321123321", "equipment": {}}}

    import json
    with open('res/strings/en-Uk/spells.json','r') as f:
        spells = json.load(f)

    print("RIGHT ------------")

    text = "cast Fireball spell on Dummy"
    print(processSpell(spells, caster["1"], text))

    text = "Cast Calm spell on Dummy"
    print(processSpell(spells, caster["1"], text))

    text = "Cast Heal spell on Dummy"
    print(processSpell(spells, caster["1"], text))

    text = "Cast Invisibility spell"
    print(processSpell(spells, caster["1"], text))

    text = "Sing Song of storms"
    print(processSpell(spells, caster["1"], text))

    text = "Pray for reference"
    print(processSpell(spells, caster["1"], text))

    text = "pray for reference"
    print(processSpell(spells, caster["1"], text))

    print("WRONG -------------"

    text = "Pray for teference"
    print(processSpell(spells, caster["1"], text))

    text = "Cast for reference"
    print(processSpell(spells, caster["1"], text))

    text = "Sing fireball spell on Dummy"
    print(processSpell(spells, caster["1"], text))

    text = "Cast Song of Storms"
    print(processSpell(spells, caster["1"], text))
