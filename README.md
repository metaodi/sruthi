[![PyPI Version](https://img.shields.io/pypi/v/sruthi)](https://pypi.org/project/sruthi/)
[![Tests + Linting Python](https://github.com/metaodi/sruthi/actions/workflows/lint_python.yml/badge.svg)](https://github.com/metaodi/sruthi/actions/workflows/lint_python.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# sruthi

**sru**thi is a client for python to make [SRU requests (Search/Retrieve via URL)](http://www.loc.gov/standards/sru/).

Currently only **SRU 1.1 and 1.2** is supported.

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
    * [`searchretrieve` operation](#searchretrieve-operation)
    * [`explain` operation](#explain-operation)
    * [Request for SRU 1.1](#request-for-sru-11)
* [Schemas](#schemas)
* [Development](#development)
* [Release](#release)

## Installation

[sruthi is available on PyPI](https://pypi.org/project/sruthi/), so to install it simply use:

```
$ pip install sruthi
```

## Usage

See the [`examples` directory](https://github.com/metaodi/sruthi/tree/master/examples) for more scripts.

### `searchretrieve` operation

```python
>>> import sruthi
>>> records = sruthi.searchretrieve('https://suche.staatsarchiv.djiktzh.ch/SRU/', query='Brettspiel')
>>> print(records)
SearchRetrieveResponse(sru_version='1.2',count=500,next_start_record=11)
>>> print(records.count)
4
>>> print(record[0])
{'schema': 'isad', 'reference': 'PAT 2, 54 d, Nr. 253492', 'title': 'Schlumberger, Jean, Zürich: Brettspiel', 'date': '08.03.1946', 'descriptionlevel': 'Dossier', 'extent': None, 'creator': None, 'extra': {'score': '0.4', 'link': 'https://suche.staatsarchiv.djiktzh.ch/detail.aspx?Id=1114641', 'beginDateISO': '1946-03-08', 'beginApprox': '0', 'endDateISO': '1946-03-08', 'endApprox': '0', 'hasDigitizedItems': '0'}}
>>>
>>> for record in records:
...    # print fields from schema
...    print(record['reference'])
...    print(record['title'])
...    print(record['date'])
...    print(record['extra']['link']) # extra record data is available at the 'extra' key
PAT 2, 54 d, Nr. 253492
Schlumberger, Jean, Zürich: Brettspiel
08.03.1946
https://suche.staatsarchiv.djiktzh.ch/detail.aspx?Id=1114641
PAT 2, 54 d, Nr. 246025
Frei, K. H., Weisslingen: Brettspiel
26.10.1945
https://suche.staatsarchiv.djiktzh.ch/detail.aspx?Id=1114639
DS 107.2.37
UZH Magazin
Die Wissenschaftszeitschrift
2019
https://suche.staatsarchiv.djiktzh.ch/detail.aspx?Id=4612939
G I 1, Nr. 34
Verordnung der Stadt Zürich betreffend die Erfüllung von Amtspflichten durch die Chorherren des Grossmünsterstifts
24.09.1485
https://suche.staatsarchiv.djiktzh.ch/detail.aspx?Id=3796980
```

The return value of `searchretrieve` is iterable, so you can easily loop over it.
Or you can use indices to access records, e.g. `records[1]` to get the second record, or `records[-1]` to get the last one.

Even [slicing](https://python-reference.readthedocs.io/en/latest/docs/brackets/slicing.html) is supported, so you can do things like only iterate over the first 5 elements using

```python
for records in records[:5]:
   print(record)
```

### `explain` operation

The `explain` operation returns a dict-like object.
The values can either be accessed as keys `info['sru_version']` or as attributes `info.sru_version`.

```python
>>> import sruthi
>>> info = sruthi.explain('https://suche.staatsarchiv.djiktzh.ch/SRU/')
>>> info
{'sru_version': '1.2', 'server': {'host': 'https://suche.staatsarchiv.djiktzh.ch/Sru', 'port': 80, 'database': 'sru'}, 'database': {'title': 'Staatsarchiv Zürich Online Search', 'description': 'Durchsuchen der Bestände des Staatsarchiv Zürichs.', 'contact': 'staatsarchivzh@ji.zh.ch'}, 'index': {'isad': {'title': 'Title', 'reference': 'Reference Code', 'date': 'Date', 'descriptionlevel': 'Level'}}, 'schema': {'isad': {'identifier': 'http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd', 'name': 'isad', 'title': 'ISAD(G)'}}, 'config': {'maximumRecords': 99, 'defaults': {'numberOfRecords': 99}}}
>>> info.server
{'host': 'https://suche.staatsarchiv.djiktzh.ch/Sru', 'port': 80, 'database': 'sru'}
>>> info.database
{'title': 'Staatsarchiv Zürich Online Search', 'description': 'Durchsuchen der Bestände des Staatsarchiv Zürichs.', 'contact': 'staatsarchivzh@ji.zh.ch'}
>>> info['index']
{'isad': {'title': 'Title', 'reference': 'Reference Code', 'date': 'Date', 'descriptionlevel': 'Level'}}
>>> info['schema']
{'isad': {'identifier': 'http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd', 'name': 'isad', 'title': 'ISAD(G)'}}
```

### Request for SRU 1.1

By default sruthi uses SRU 1.2 to make requests, but you can specify the SRU version for each call or when you create a new client instance:

```python
>>> import sruthi
>>> # create a client
>>> client = sruthi.Client(
...     'https://services.dnb.de/sru/dnb',
...     record_schema='oai_dc',
...     sru_version='1.1'
>>> )
>>> records = client.searchretrieve(query="Zurich")
>>> records.count
8985
>>> # ...or pass the version directly to the call
>>> records = sruthi.searchretrieve(
...     'https://services.dnb.de/sru/dnb',
...     query="Zurich",
...     record_schema='oai_dc',
...     sru_version='1.1'
>>> )
>>> records.count
8985
```

### Custom parameters and settings

If an SRU endpoint needs additional (custom) parameters, you can create your own session object and pass it to the client.
This is useful for adding authentication (username, password), custom headers or parameters, SSL verification settings etc.

```python
>>> import sruthi
>>> import requests
>>> # customize session
>>> session = requests.Session()
>>> session.params = {"x-collection": "GGC"}
>>> # pass the customized session to sruthi
>>> records = sruthi.searchretrieve("https://jsru.kb.nl/sru", query="gruninger", session=session)
>>> records.count
4
```

## Schemas

sruthi does not make any assumptions about the record data schema.
The data is provided as-is (as a flattend dict).
sruthi has been tested with the following schemas:

* [Dublin Core Record Schema](http://www.loc.gov/standards/sru/recordSchemas/dc-schema.html) (dc)
* [MARCXML: The MARC 21 XML Schema](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd) (marcxml)
* [ISAD(G): General International Standard Archival Description, Second edition](http://www.expertisecentrumdavid.be/xmlschemas/isad.xsd) (isad)

## Development

To contribute to sruthi simply clone this repository and follow the instructions in [CONTRIBUTING.md](/CONTRIBUTING.md).

This project has a `Makefile` with the most common commands.
Type `make help` to get an overview.

## Release

To create a new release, follow these steps (please respect [Semantic Versioning](http://semver.org/)):

1. Adapt the version number in `sruthi/__init__.py`
1. Update the CHANGELOG with the version
1. Create a pull request to merge `develop` into `master` (make sure the tests pass!)
1. Create a [new release/tag on GitHub](https://github.com/metaodi/sruthi/releases) (on the master branch)
1. The [publication on PyPI](https://pypi.python.org/pypi/sruthi) happens via [GitHub Actions](https://github.com/metaodi/sruthi/actions?query=workflow%3A%22Upload+Python+Package%22) on every tagged commit
