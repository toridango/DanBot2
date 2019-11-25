import requests

def get_GDQuote():
    url = "https://taskinoz.com/gdq/api/"
    r = requests.get(url)
    if r.status_code != 200:
        return "Error {code} while trying to access {url}".format(code=r.status_code, url=url)
    return r.content.decode()

if __name__ == "__main__":
    print(get_GDQuote())
