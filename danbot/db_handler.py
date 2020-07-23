import json
import os

RES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")


def get_resource_path(resource):
    return os.path.join(RES_DIR, resource)


def get_strings_resource_path(resource, lang="en-uk"):
    return get_resource_path(os.path.join("strings", lang, resource))


RES_PATHS = {
    "strings": get_strings_resource_path("strings.json"),
    "spells": get_strings_resource_path("spells.json"),
    "global": get_resource_path("global.json"),
    "keys": get_resource_path("keys.json"),
    "users": get_resource_path("users.json"),
}


def load_resource(resource):
    """ Reads json resource and returns the raw contents """
    if resource not in RES_PATHS:
        raise Exception(f"Unknown resource: {resource}")

    with open(RES_PATHS[resource], 'r', encoding='utf8') as f:
        data = json.load(f)

    return data


def save_resource(resource, data):
    """ Saves json resource from data structure into disk """
    if resource not in RES_PATHS:
        raise Exception(f"Unknown resource: {resource}")

    with open(RES_PATHS[resource], 'w', encoding='utf8') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))


def get_quotes():
    quotes_file = get_resource_path("quotes.txt")

    with open(quotes_file, 'r', encoding="utf-8") as f:
        data = f.read()
        data = data.split("\n\n")
        for i, elem in enumerate(data):
            st = elem.find('"')
            en = elem.find('"', st + 3)
            data[i] = elem[st + 1:en]

    return data
