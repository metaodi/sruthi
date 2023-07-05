import os
import requests
from sruthi import Client

# create authenticated session
user = os.getenv('CATALOG_USER')
pw = os.getenv('CATALOG_PASS')
session = requests.Session()
session.auth = (user, pw)

# pass authenticated session to client
sru_client = Client('https://suche.staatsarchiv.djiktzh.ch/SRU/', session=session)

# get records for query
records = sru_client.searchretrieve(query='Zürich')
print(records)
