import db_handler as db

def nested_get(dict, keys):    
    for key in keys:
        dict = dict[key]
    return dict

# navigate until penultimate key depth, get dict therein (or initialise it), set the last key in the list to the given value
def nested_set(dict, keys, value):
    for key in keys[:-1]:
        dict = dict.setdefault(key, {}) # setdefault: return the value of the item under <key>, or insert empty dictionary if it doesn't exist
    dict[keys[-1]] = value

def add_user_entry(users, new_entry_path, value):
    for user, user_dict in users.items():
        nested_set(user_dict, new_entry_path, value)

def clone_user_entry(users, entry_path, clone_path):
    for user, user_dict in users.items():
        nested_set(user_dict, clone_path, nested_get(user_dict, entry_path))


def make_jackpotcoins():
    users = db.load_resource("users")
    clone_user_entry(users, ["inventory", "coins"], ["inventory", "jackpotcoins"])
    db.save_resource("users", users)

def test_make_jackpotcoins():
    make_jackpotcoins()
    users = db.load_resource("users")
    for user, user_dict in users.items():
        print(user_dict)

def test():
    users = db.load_resource("users")
    for user, user_dict in users.items():
        print(user_dict)
    print("\n------------------------------------------------\n")

    clone_user_entry(users, ["inventory", "coins"], ["inventory", "testcoins"])
    for user, user_dict in users.items():
        print(user_dict)
    print("\n------------------------------------------------\n")

    add_user_entry(users, ["properties", "insight"], 99)
    for user, user_dict in users.items():
        print(user_dict)

if __name__ == "__main__":
    # test()
    # test_make_jackpotcoins()
    
    
    pass