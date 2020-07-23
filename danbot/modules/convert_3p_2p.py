"""
@author: Daniel Gomez-Casañ
@date: 14 March 2019
@desc: This module converts 3rd person "tell-them-this" sentences into 2nd person "this" sentences
Basically like pettily trying to ignore someone and still talk to them through a third individual, but sarcastically, of course (?)

Disclaimer: this was hacked in a short time and patched later in a rush
"""


def case_apostrophe(word_list):
    new_list = []
    for i, w in enumerate(word_list):
        new_word = w
        if w in ["she's", "he's", "they're"]:
            if word_list[i + 1] == "got":
                new_word = "you've"
            else:
                new_word = "you're"
        elif w == "they've":
            new_word = "you've"

        new_list.append(new_word)

    return new_list


def fix_after_pronouns(word_list):
    new_list = []
    for i, w in enumerate(word_list):
        new_word = w
        if word_list[i - 1] in ["she", "he", "they"]:
            if w == "is":
                new_word = "are"
            elif w[-1] == "s":
                new_word = w[:-1]

        new_list.append(new_word)

    return new_list


def fix_extra_pronouns(word_list):
    out_list = ["yourself" if w in ["herself", "himself", "themselves"] else w for w in word_list]
    return ["your" if w in ["her", "him", "their"] else w for w in out_list]


def convert_3p_to_2p(sentence, author="someone", cmd_start="tell", author_pronoun="me"):
    l_sentence = sentence.lower()
    word_list = (sentence.split(" "))
    # print(word_list)
    out_list = []

    # tuple: (pos withing parent string, substring)
    auxStr = (
        l_sentence.find(cmd_start) + len(cmd_start) + 1, l_sentence[l_sentence.find(cmd_start) + len(cmd_start) + 1:])

    # first word after the command and capitalise the first letter
    targ = auxStr[1][:auxStr[1].find(" ")]
    out_list.append(targ.title() + ",")

    # find first occurence of target in word list
    targ_pos = [i for i, w in enumerate(word_list) if targ == w]
    # print(targ_pos)

    # find 3rd person pronoun
    pro_pos = [i for i, w in enumerate(word_list) if w.lower() in ["she", "he", "they"]]
    # print(pro_pos)

    # find 3rd person pronoun with an included verb
    sp_pro_pos = [i for i, w in enumerate(word_list) if w.lower() in ["she's", "he's", "they're", "they've"]]
    # print(sp_pro_pos)

    # find "to"
    other_case_pos = [i for i, w in enumerate(word_list) if w.lower() in ["to", "that", "can"]]
    # print(other_case_pos)

    len_pro_pos = len(pro_pos)
    len_sp_pro_pos = len(sp_pro_pos)
    len_other_case_pos = len(other_case_pos)

    index_list = []
    case = -1

    # if it was found, enter the competition
    if len_pro_pos > 0:
        index_list.append(pro_pos[0])
    if len_sp_pro_pos > 0:
        index_list.append(sp_pro_pos[0])
    if len_other_case_pos > 0:
        index_list.append(other_case_pos[0])

    # whoever's the first gets chosen as the case
    if len_pro_pos > 0 and pro_pos[0] == min(index_list):
        case = 0
    elif len_sp_pro_pos > 0 and sp_pro_pos[0] == min(index_list):
        case = 1
    elif len_other_case_pos > 0 and other_case_pos[0] == min(index_list):
        case = 2

    # print("case", case)

    # pronoun found case
    if case == 0:
        out_list.append("you")

        rest = [w[:-1] if w[-1].lower() == "s" else w for w in word_list[pro_pos[0] + 1:]]
        # print(rest)

        out_list += rest
        fix_extra_pronouns(out_list)
    elif case == 1:
        # I would make this a map but I need to look ahead
        rest = case_apostrophe(word_list[sp_pro_pos[0]:])
        out_list += rest
        fix_extra_pronouns(out_list)

    elif case == 2:
        # detect if next two are "to tell", if so, delete "to" and add the rest raw
        if word_list[other_case_pos[0] + 1] == "tell":
            out_list += word_list[other_case_pos[0] + 1:]
        else:
            # print("not tell")
            word_list = fix_after_pronouns(word_list)
            # Pronouns are being changed for the more usual cases, so "tell <X> to tell <Y> that they <Z>" cases won't work
            rest = ["you" if w.lower() in ["she", "he", "they"] else w for w in word_list[other_case_pos[0] + 1:]]
            # print(rest)

            out_list += rest
            out_list = fix_extra_pronouns(out_list)

    if targ == "them":
        out_list = [w[0].upper() + w[1:] if "you" in w.lower() else w for w in out_list[1:]]

    return " ".join([author if w == author_pronoun else w for w in out_list])


if __name__ == "__main__":
    print(convert_3p_to_2p("Tell A he sucks"))
    print(convert_3p_to_2p("Tell B she still owes me lunch", "T"))
    print(convert_3p_to_2p("Tell B she should make it double"))
    print(convert_3p_to_2p("Tell C they can make it"))
    print(convert_3p_to_2p("Tell M to eat shit"))

    print(convert_3p_to_2p("Tell them they are not funny"))
    print(convert_3p_to_2p("Tell them they've got it wrong"))
    print(convert_3p_to_2p("Tell R he's not funny"))
    print(convert_3p_to_2p("Tell R he's got zero sense of humour"))
    print(convert_3p_to_2p("Tell R he's never going to die"))
    print(convert_3p_to_2p("Tell them they're wrong"))
    print(convert_3p_to_2p("Tell them they've got nothing to win from that"))

    print(convert_3p_to_2p("Tell D she's being all loud and shit and we're in class"))
    print(convert_3p_to_2p("Tell T to tell S that she is being a jerk"))
    print(convert_3p_to_2p("Tell T to shower because he smells"))
    print(convert_3p_to_2p("Tell D to stop herself from thinking ficticious characters are her family"))
    print(convert_3p_to_2p("Tell A to tell B to tell C to tell D I'm stupid"))
    print(convert_3p_to_2p("Tell B to tell C to tell D I'm stupid"))
    print(convert_3p_to_2p("Tell C to tell D I'm stupid"))
