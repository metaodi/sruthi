# -*- coding: utf-8 -*-

from collections import defaultdict
import re
from . import xmlparse
from . import errors

class SruData(object):
    def __init__(self, records=[], sru_version=None, count=0, data_loader=None):
        self.records = records
        self.sru_version = sru_version
        self.count = count
        self._data_loader = data_loader
    
    def __repr__(self):
        return (
            'SruData('
            'sru_version=%r,'
            'count=%r,'
            'records=%r)'
            ) % (
               self.sru_version,
               self.count,
               self.records
            )

    def __length_hint__(self):
        return self.count

    def __iter__(self):
        # use while loop since self.records could grow while iterating
        i = 0 
        while True:
            # load new data when near end
            if i == len(self.records):
                try:
                    result = self._data_loader()
                    print(result)
                    self.records.extend(result['records'])
                except errors.NoMoreRecordsError:
                    break
            yield self.records[i]
            i += 1  

    def __getitem__(self, key):
        return self.records[key]


def extract_records(xml):
    records = []

    xml_recs = xmlparse.findall(xml, './sru:records/sru:record')
    for xml_rec in xml_recs:
        record = defaultdict()
        record['schema'] = xmlparse.find(xml_rec, './sru:recordSchema').text
        record_data = xmlparse.find(xml_rec, './sru:recordData')
        extra_data = xmlparse.find(xml_rec, './sru:extraRecordData')
        
        for elem in record_data.iter():
            record = tag_data(record, elem)

        extra = defaultdict()
        for elem in extra_data.iter():
            extra = tag_data(extra, elem)
        record['extra'] = dict(extra)

        record.pop('recordData', None)
        record.pop('extraRecordData', None)

        record = dict(record)
        records.append(record)
    return records


def tag_data(record, elem):
    ns_pattern = re.compile('{.+}')
    tag_name = ns_pattern.sub('', elem.tag)
    if elem.text and elem.text.strip():
        record[tag_name] = elem.text.strip()
    elif len(list(elem)) == 0: # leaf element
        record[tag_name] = None
    return record
