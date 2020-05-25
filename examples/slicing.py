import sruthi

records = sruthi.searchretrieve('https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Zurich')

print("records.count:", records.count)
print("len(records.records):", len(records.records))
print("records[0]:", records[0]) # print the first record
print("records[-1]:", records[-1]) # print the last record
print("records[-200]:", records[-200]) # print the 200th record from the end
print("records[410]:", records[410]) # print record at index 410
print("records[:5]:", records[:5]) # print the first 5 records
print("records[6:20:2]:", records[6:20:2]) # print every second record from 6-20
