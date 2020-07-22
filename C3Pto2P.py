"""
@author: Daniel Gomez-Casañ
@date: 14 March 2019
@desc: This module converts 3rd person "tell-them-this" sentences into 2nd person "this" sentences
Basically like pettily trying to ignore someone and still talk to them through a third individual, but sarcastically, of course (?)

Disclaimer: this was hacked in a short time and patched later in a rush
"""


def CaseApostrophe(wordList):
    newList = []
    for i, w in enumerate(wordList):
        newWord = w
        if w in ["she's", "he's", "they're"]:
            if wordList[i + 1] == "got":
                newWord = "you've"
            else:
                newWord = "you're"
        elif w == "they've":
            newWord = "you've"

        newList.append(newWord)

    return newList


def FixAfterPronouns(wordList):
    newList = []
    for i, w in enumerate(wordList):
        newWord = w
        if wordList[i - 1] in ["she", "he", "they"]:
            if w == "is":
                newWord = "are"
            elif w[-1] == "s":
                newWord = w[:-1]

        newList.append(newWord)

    return newList


def FixExtraPronouns(wordList):
    outList = [(lambda w: "yourself" if w in ["herself", "himself", "themselves"] else w)(w) for i, w in
               enumerate(wordList)]
    return [(lambda w: "your" if w in ["her", "him", "their"] else w)(w) for i, w in enumerate(outList)]


def convert3Pto2P(sentence, author="someone", cmdStart="tell", authorPronoun="me"):
    l_sentence = sentence.lower()
    wordList = (sentence.split(" "))
    # print(wordList)
    outList = []

    # tuple: (pos withing parent string, substring)
    auxStr = (l_sentence.find(cmdStart) + len(cmdStart) + 1, l_sentence[l_sentence.find(cmdStart) + len(cmdStart) + 1:])

    # first word after the command and capitalise the first letter
    targ = auxStr[1][:auxStr[1].find(" ")]
    outList.append(targ.title() + ",")

    # find first occurence of target in word list
    targPos = [i for i, w in enumerate(wordList) if targ == w]
    # print(targPos)

    # find 3rd person pronoun
    proPos = [i for i, w in enumerate(wordList) if w.lower() in ["she", "he", "they"]]
    # print(proPos)

    # find 3rd person pronoun with an included verb
    spProPos = [i for i, w in enumerate(wordList) if w.lower() in ["she's", "he's", "they're", "they've"]]
    # print(proPos)

    # find "to"
    otherCasePos = [i for i, w in enumerate(wordList) if w.lower() in ["to", "that", "can"]]
    # print(otherCasePos)

    lenProPos = len(proPos)
    lenSpProPos = len(spProPos)
    lenOtherCasePos = len(otherCasePos)

    indexList = []
    case = -1

    # if it was found, enter the competition
    if lenProPos > 0:
        indexList.append(proPos[0])
    if lenSpProPos > 0:
        indexList.append(spProPos[0])
    if lenOtherCasePos > 0:
        indexList.append(otherCasePos[0])

    # whoever's the first gets chosen as the case
    if (lenProPos > 0 and proPos[0] == min(indexList)):
        case = 0
    elif (lenSpProPos > 0 and spProPos[0] == min(indexList)):
        case = 1
    elif (lenOtherCasePos > 0 and otherCasePos[0] == min(indexList)):
        case = 2

    # print("case", case)

    # pronoun found case
    if (case == 0):

        outList.append("you")

        rest = [(lambda w: w[:-1] if w[-1].lower() == "s" else w)(w) for i, w in enumerate(wordList[proPos[0] + 1:])]
        # print(rest)

        outList += rest
        FixExtraPronouns(outList)

    elif (case == 1):

        # I would make this a map but I need to look ahead
        rest = CaseApostrophe(wordList[spProPos[0]:])
        outList += rest
        FixExtraPronouns(outList)

    elif (case == 2):

        # detect if next two are "to tell", if so, delete "to" and add the rest raw
        if wordList[otherCasePos[0] + 1] == "tell":
            outList += wordList[otherCasePos[0] + 1:]
        else:
            # print("not tell")
            wordList = FixAfterPronouns(wordList)
            # Pronouns are being changed for the more usual cases, so "tell <X> to tell <Y> that they <Z>" cases won't work
            rest = [(lambda w: "you" if w.lower() in ["she", "he", "they"] else w)(w) for i, w in
                    enumerate(wordList[otherCasePos[0] + 1:])]
            # print(rest)

            outList += rest
            outList = FixExtraPronouns(outList)

    if (targ == "them"):
        outList = [(lambda w: w[0].upper() + w[1:] if "you" in w.lower() else w)(w) for i, w in enumerate(outList[1:])]

    return " ".join([(lambda w: author if w == authorPronoun else w)(w) for i, w in enumerate(outList)])


if __name__ == "__main__":
    print(convert3Pto2P("Tell A he sucks"))
    print(convert3Pto2P("Tell B she still owes me lunch", "T"))
    print(convert3Pto2P("Tell B she should make it double"))
    print(convert3Pto2P("Tell C they can make it"))
    print(convert3Pto2P("Tell M to eat shit"))

    print(convert3Pto2P("Tell them they are not funny"))
    print(convert3Pto2P("Tell them they've got it wrong"))
    print(convert3Pto2P("Tell R he's not funny"))
    print(convert3Pto2P("Tell R he's got zero sense of humour"))
    print(convert3Pto2P("Tell R he's never going to die"))
    print(convert3Pto2P("Tell them they're wrong"))
    print(convert3Pto2P("Tell them they've got nothing to win from that"))

    print(convert3Pto2P("Tell D she's being all loud and shit and we're in class"))
    print(convert3Pto2P("Tell T to tell S that she is being a jerk"))
    print(convert3Pto2P("Tell T to shower because he smells"))
    print(convert3Pto2P("Tell D to stop herself from thinking ficticious characters are her family"))
    print(convert3Pto2P("Tell A to tell B to tell C to tell D I'm stupid"))
    print(convert3Pto2P("Tell B to tell C to tell D I'm stupid"))
    print(convert3Pto2P("Tell C to tell D I'm stupid"))
