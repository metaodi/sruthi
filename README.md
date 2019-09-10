# sruthie

**sru**thie is a client for python to make [SRU requests (Search/Retrieve via URL)](http://www.loc.gov/standards/sru/).

## Contents

* [Usage](#usage)
* [Schemas](#schemas)

## Usage

```python
import sruthie

records = sruthie.searchretrieve('https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Zurich')

for record in records:
    # print fields from schema
    print(record['reference'])
    print(record['title'])
    print(record['date'])
    print(record['extra']['link']) # extra record data is available at the 'extra' key
```

```python
# you can get more information at each step
import sruthie

# note: records is an iterator
records = sruthie.searchretrieve'https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Human')
print(records.cql)
print(records.sru_version)
print(records.count)

for record in records:
    print(record)
    print(record['schema'])
```

```python
import sruthie

info = sruthie.explain('https://suche.staatsarchiv.djiktzh.ch/SRU/')
print(info.server)
print(info.database)
print(info.index)
print(info.schema)
```



## Schemas

Currently the following schemas are supported by sruthie. Altough 

* [Dublin Core Record Schema](http://www.loc.gov/standards/sru/recordSchemas/dc-schema.html) (dc)
* [MARCXML: The MARC 21 XML Schema](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd) (marcxml)
* [ISAD(G): General International Standard Archival Description, Second edition](http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd) (isad)
