'''
@author: Daniel Gomez-Casañ
@date: 14 March 2019
@desc: This module converts 3rd person "tell-them-this" sentences into 2nd person "this" sentences
Basically like pettily trying to ignore someone and still talk to them through a third individual, but sarcastically, of course (?)
'''

def CaseApostrophe(wordList):
    
    newList = []
    for i, w in enumerate(wordList):
        newWord = w
        if w in ["she's", "he's", "they're"]:
            if wordList[i+1] == "got":
                newWord = "you've"
            else:
                newWord = "you're"
        elif w == "they've":
            newWord = "you've"
            
        newList.append(newWord)

    return newList


def convert3Pto2P(sentence, author = "someone" , cmdStart = "tell", authorPronoun = "me"):
    l_sentence = sentence.lower()
    wordList = (l_sentence.split(" "))
    # print(wordList)
    outList = []


    # tuple: (pos withing parent string, substring)
    auxStr = (l_sentence.find(cmdStart) + len(cmdStart) + 1, l_sentence[l_sentence.find(cmdStart) + len(cmdStart) + 1 :])

    # first word after the command and capitalise the first letter
    targ = auxStr[1][:auxStr[1].find(" ")]
    outList.append(targ.title() + ",")

    # find first occurence of target in word list
    targPos = [i for i, w in enumerate(wordList) if targ == w]
    # print(targPos)

    # find 3rd person pronoun
    proPos = [i for i, w in enumerate(wordList) if w in ["she", "he", "they"]]
    # print(proPos)
    
    # find 3rd person pronoun with an included verb
    spProPos = [i for i, w in enumerate(wordList) if w in ["she's", "he's", "they're", "they've"]]
    # print(proPos)
    
    # find "to"
    otherCasePos = [i for i, w in enumerate(wordList) if w in ["to", "that", "can"]]
    # print(otherCasePos)

    # pronoun found case
    if (len(proPos) > 0):
    
        outList.append("you")

        rest = [(lambda w: w[:-1] if w[-1] == "s" else w)(w) for i, w in enumerate(wordList[proPos[0] + 1:])]
        # print(rest)

        outList += rest
        
    elif (len(spProPos) > 0):

        # I would make this a map but I need to look ahead
        rest = CaseApostrophe(wordList[spProPos[0]:])
        outList += rest

    elif (len(otherCasePos) > 0):
        
        rest = [(lambda w: "you" if w in ["she", "he", "they"] else w)(w) for i, w in enumerate(wordList[otherCasePos[0] + 1:])]
        # print(rest)

        outList += rest

    if (targ == "them"):
        outList = [(lambda w: w[0].upper()+w[1:] if "you" in w else w)(w) for i, w in enumerate(outList[1:])]
        

    return " ".join([(lambda w: author if w == authorPronoun else w)(w) for i, w in enumerate(outList)])


if __name__ == "__main__":
    print(convert3Pto2P("Tell John he sucks"))
    print(convert3Pto2P("Tell Anna she still owes me lunch", "Tim"))
    print(convert3Pto2P("Tell Sarah she should make it double"))
    print(convert3Pto2P("Tell Max they can make it"))
    print(convert3Pto2P("Tell Rajoy to eat shit"))

    print(convert3Pto2P("Tell them they are not funny"))
    print(convert3Pto2P("Tell them they've got it wrong"))
    print(convert3Pto2P("Tell Ruby he's not funny"))
    print(convert3Pto2P("Tell Ruby he's got zero sense of humour"))
    print(convert3Pto2P("Tell Ruby he's never going to die"))
    print(convert3Pto2P("Tell them they're wrong"))
    print(convert3Pto2P("Tell them they've got nothing to win from that"))