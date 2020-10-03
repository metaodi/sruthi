import sruthi
from pprint import pprint

# check supported schemas of server
server_url = 'https://suche.staatsarchiv.djiktzh.ch/SRU/'
schema = 'isad'
server = sruthi.explain(server_url)


print(20 * '=')
print('=')
print(f"= Record with schema: {schema}")
print('=')
print(20 * '=')
records = sruthi.searchretrieve(
    server_url,
    query='Zurich',
    record_schema=schema
)
pprint(records[0])
