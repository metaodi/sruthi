import requests
import sruthi
from pprint import pprint


def print_url(r, *args, **kwargs):
    print(r.url)


# create session with custom paramter session
session = requests.Session()

# here some example of how a session can be used to customize parameters, settings etc.
session.params = {"x-collection": "GGC"}  # add custom request parameter
session.verify = False  # disable SSL verfications
session.hooks["response"].append(print_url)  # add custom hook

# pass custom session to client
sru_client = sruthi.Client("https://jsru.kb.nl/sru", session=session)

# get records for query
records = sru_client.searchretrieve(query="gruninger")
pprint(records)
print("---")
pprint(records[0])
