from sruthi import Client

# create a new client and call explain()
sru_client = Client("https://suche.staatsarchiv.djiktzh.ch/SRU/")
info = sru_client.explain()

for name, details in info.schema.items():
    print(f"This SRU endpoint supports the metadata schema {details['title']}.")

# configure the maximum records based on the config
try:
    sru_client.maximum_records = info.config["maximumRecords"]
    print(f"Set maximum_records to {sru_client.maximum_records}.")
except KeyError:
    print("Config `maximum_records` not available, keep original value")

# get records for query
records = sru_client.searchretrieve(query="Zürich")

# display 5 records
print("")
print("First 5 results for `Zürich`")
for r in records[:5]:
    print("* ", r["title"])
