# -*- coding: utf-8 -*-

from collections import defaultdict
import re
from . import xmlparse

class SruData(object):
    def __init__(self, records=[], sru_version=None, count=0):
        self.records = records
        self.sru_version = sru_version
        self.count = count
    
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

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        # use while loop since self.records could grow while iterating
        i = 0  
        while i < len(self.records):  
            yield self.records[i]
            i += 1  
            # TODO: check if is near the end and load more records (lazy loading)

    def __getitem__(self, key):
        return self.records[key]

    def add_records(self, new_records):
        self.record.extend(new_records)


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
