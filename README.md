# sruthi

**sru**thi is a client for python to make [SRU requests (Search/Retrieve via URL)](http://www.loc.gov/standards/sru/).

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Schemas](#schemas)

## Installation

[sruthi is available on PyPI](https://pypi.org/project/sruthi/), so to install it simply use:

```
$ pip install sruthi
```

## Usage

### `searchretrieve` operation

```python
import sruthi

records = sruthi.searchretrieve('https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Zurich')

for record in records:
    # print fields from schema
    print(record['reference'])
    print(record['title'])
    print(record['date'])
    print(record['extra']['link']) # extra record data is available at the 'extra' key
```

```python
# you can get more information at each step
import sruthi

# note: records is an iterator
records = sruthi.searchretrieve('https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Human')
print(records.cql)
print(records.sru_version)
print(records.count)

for record in records:
    print(record)
    print(record['schema'])
```

The return value of `searchretrieve` is iterable, so you can easily loop over it. Or you can use indices to access elements, e.g. `records[1]` to get the second elemenet, or `records[-1]` to get the last one.

Even [slicing](https://python-reference.readthedocs.io/en/latest/docs/brackets/slicing.html) is supported, so can can do things like only iterate over the first 5 elements using

```python
for records in records[:5]:
   print(record)
```

### `explain` operation

```python
import sruthi

info = sruthi.explain('https://suche.staatsarchiv.djiktzh.ch/SRU/')
print(info.server)
print(info.database)
print(info.index)
print(info.schema)
```




## Schemas

sruthi does not make any assumptions about the record data schema.
The data is provided as-is (as a flattend dict).
sruthi has been tested with the following schemas:

* [Dublin Core Record Schema](http://www.loc.gov/standards/sru/recordSchemas/dc-schema.html) (dc)
* [MARCXML: The MARC 21 XML Schema](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd) (marcxml)
* [ISAD(G): General International Standard Archival Description, Second edition](http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd) (isad)
