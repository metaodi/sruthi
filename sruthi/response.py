# -*- coding: utf-8 -*-

from collections import defaultdict
import re
from . import xmlparse
from . import errors

class Response(object):
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.records = []
        xml = self.data_loader.load()
        self._parse_content(xml)

    def _check_response_tag(self, xml, tag):
        sru = '{http://www.loc.gov/zing/srw/}'
        response = f"{sru}{tag}"
        if not xml.tag == response:
            raise errors.ServerIncompatibleError(
                f"Server response did not contain a {response} tag"
            )


class SearchRetrieveResponse(Response):
    def __repr__(self):
        try: 
            return (
                'SearchRetrieveResponse('
                'count=%r,'
                'next_start_record=%r'
                'records=%r)'
                ) % (
                   self.count,
                   self.next_start_record,
                   self.records
                )
        except AttributeError:
            return 'SearchRetrieveResponse(empty)'

    def _parse_content(self, xml):
        self._check_response_tag(xml, 'searchRetrieveResponse')

        self.sru_version = xmlparse.find(xml, './sru:version').text
        self.count = int(xmlparse.find(xml, './sru:numberOfRecords').text)
        self._extract_records(xml)

        next_start_record = xmlparse.find(xml, './sru:nextRecordPosition').text
        if next_start_record:
            self.next_start_record = int(next_start_record)
        else:
            self.next_start_record = None

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
        xml = self.data_loader.load(startRecord=self.next_start_record)
        self._parse_content(xml)
        if self.next_start_record is None:
            raise errors.NoMoreRecordsError()

    def _extract_records(self, xml):
        new_records = []

        xml_recs = xmlparse.findall(xml, './sru:records/sru:record')
        for xml_rec in xml_recs:
            record = defaultdict()
            record['schema'] = xmlparse.find(xml_rec, './sru:recordSchema').text
            record_data = xmlparse.find(xml_rec, './sru:recordData')
            extra_data = xmlparse.find(xml_rec, './sru:extraRecordData')

            for elem in record_data.iter():
                record = self._tag_data(record, elem)

            extra = defaultdict()
            for elem in extra_data.iter():
                extra = self._tag_data(extra, elem)
            record['extra'] = dict(extra)

            record.pop('recordData', None)
            record.pop('extraRecordData', None)

            record = dict(record)
            new_records.append(record)
        self.records.extend(new_records)

    def _tag_data(self, record, elem):
        ns_pattern = re.compile('{.+}')
        tag_name = ns_pattern.sub('', elem.tag)
        if elem.text and elem.text.strip():
            record[tag_name] = elem.text.strip()
        elif len(list(elem)) == 0:  # leaf element
            record[tag_name] = None
        return record


class ExplainResponse(Response):
    def __repr__(self):
        return (
            'ExplainResponse('
            'sru_version=%r,'
            'server=%r,'
            'database=%r'
            'index=%r'
            'schema=%r)'
            ) % (
               self.sru_version,
               self.server,
               self.database,
               self.index,
               self.schema,
            )

    def _parse_content(self, xml):
        self._check_response_tag(xml, 'explainResponse')

        self.sru_version = xmlparse.find(xml, './sru:version').text
        self.server = xmlparse.find(xml, './zr:serverInfo').text
        self.database = ''
        self.index = ''
        self.schema = ''
        print(self)


