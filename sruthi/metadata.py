# -*- coding: utf-8 -*-

from collections import defaultdict
import re
from . import xmlparse
from . import errors


class SruData(object):
    def __init__(self, records=[], sru_version=None, count=0, data_loader=None):  # noqa
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
                    self._load_new_data()
                except errors.NoMoreRecordsError:
                    break
            yield self.records[i]
            i += 1

    def __getitem__(self, key):
        if isinstance(key, slice):
            limit = max(key.start or 0, key.stop or self.count)
            self._load_new_data_until(limit)
            count = len(self.records)
            return [self.records[k] for k in range(*key.indices(count))]

        if not isinstance(key, int):
            raise TypeError("Index must be an integer or slice")

        limit = key
        if limit < 0:
            # if we get a negative index, load all data
            limit = self.count
        self._load_new_data_until(limit)
        return self.records[key]

    def _load_new_data_until(self, limit):
        while limit >= len(self.records):
            try:
                self._load_new_data()
            except errors.NoMoreRecordsError:
                break

    def _load_new_data(self):
        result = self._data_loader()
        self.records.extend(result['records'])


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
    elif len(list(elem)) == 0:  # leaf element
        record[tag_name] = None
    return record
