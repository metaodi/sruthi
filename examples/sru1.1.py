import sruthi
from pprint import pprint

# check supported schemas of server
server_url = 'https://services.dnb.de/sru/dnb'

# create sruthi client
client = sruthi.Client(server_url, record_schema='oai_dc', sru_version='1.1')

explain = client.explain()
print(f'SRU version: {explain.sru_version}')
pprint(explain.server)
pprint(explain.config)
pprint(explain.index, depth=1)
pprint(explain.schema, depth=1)
pprint(explain.database)


print(20 * '=')
print('=')
print(f"= Record with schema: {client.record_schema}")
print('=')
print(20 * '=')
records = client.searchretrieve(
    query='Zurich'
)
print(f'Total records: {records.count}')
pprint(records[0])
