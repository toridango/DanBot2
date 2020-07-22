import json


def read_json(filepath):
    """ Reads json from filepath and returns the unadultered read contents """
    with open(filepath, 'r', encoding='utf8') as f:
        data = json.load(f)

    return data


def save_json(filename, data):
    """ Saves json from data structure into disk """
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))


def read_bingo(filename):
    global bote  # TODO where is this variable coming from??
    flag = False
    try:
        with open(filename, 'r') as f:
            data = f.read()
            data = data.split("\n")
    except:
        with open(filename, 'w+') as f:
            data = []

    print(data)
    for i, e in enumerate(data):
        if e != "":
            data[i] = int(e)
        else:
            flag = True

    if flag and data[-1] == "":
        del data[-1]

    bote = len(data) - 1
    return data


def save_bingo(filename, bingo_data):
    # print bingo_data

    with open(filename, 'w') as f:
        for i, elem in enumerate(bingo_data):
            if elem != "":
                if i == len(bingo_data) - 1:
                    f.write(str(elem))
                else:
                    f.write(str(elem) + "\n")


def get_quotes(filename):
    with open(filename, 'r') as f:
        data = f.read()
        data = data.split("\n\n")
        for i, elem in enumerate(data):
            st = elem.find('"')
            en = elem.find('"', st + 3)
            data[i] = elem[st + 1:en]

    return data


def get_keys_data(filepath, targets):
    """ Gets the data from the json key data file and returns the target parameter """
    data = read_json(filepath)
    values = []

    for t in targets:
        if t in data:
            values.append(data[t])

    return values
