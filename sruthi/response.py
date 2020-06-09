# -*- coding: utf-8 -*-

from collections import defaultdict
import re
import warnings
from . import xmlparse
from . import errors


class Response(object):
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.xmlparser = xmlparse.XMLParser()
        self.records = []
        xml = self.data_loader.load()
        self._parse_content(xml)

    def maybe_int(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return s

    def _check_response_tag(self, xml, tag):
        sru = '{http://www.loc.gov/zing/srw/}'
        response = f"{sru}{tag}"
        if not xml.tag == response:
            # fix namespace for servers that provide the wrong namespace URI
            main_ns = self.xmlparser.namespace(xml)
            if 'www.loc.gov/zing/srw' in main_ns:
                warnings.warn(
                    f"""
                    The server has the wrong namespace for SRU,
                    it should be {sru} but it's currently set to {{{main_ns}}}.
                    """,
                    errors.WrongNamespaceWarning
                )
                self.xmlparser.namespaces['sru'] = main_ns
            else:
                raise errors.ServerIncompatibleError(
                    f"Server response did not contain a {response} tag"
                )


class SearchRetrieveResponse(Response):
    def __repr__(self):
        try:
            return (
                'SearchRetrieveResponse('
                'sru_version=%r,'
                'count=%r,'
                'next_start_record=%r)'
                ) % (
                   self.sru_version,
                   self.count,
                   self.next_start_record,
                )
        except AttributeError:
            return 'SearchRetrieveResponse(empty)'

    def _parse_content(self, xml):
        self._check_response_tag(xml, 'searchRetrieveResponse')

        self.sru_version = self.xmlparser.find(xml, './sru:version').text
        self.count = self.maybe_int(self.xmlparser.find(xml, './sru:numberOfRecords').text)
        self._extract_records(xml)

        next_start_record = self.xmlparser.find(xml, './sru:nextRecordPosition').text
        if next_start_record:
            self.next_start_record = self.maybe_int(next_start_record)
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
        if self.next_start_record is None:
            raise errors.NoMoreRecordsError()
        xml = self.data_loader.load(startRecord=self.next_start_record)
        self._parse_content(xml)

    def _extract_records(self, xml):
        new_records = []

        xml_recs = self.xmlparser.findall(xml, './sru:records/sru:record')
        for xml_rec in xml_recs:
            record = defaultdict()
            record['schema'] = self.xmlparser.find(xml_rec, './sru:recordSchema').text
            record_data = self.xmlparser.find(xml_rec, './sru:recordData')
            extra_data = self.xmlparser.find(xml_rec, './sru:extraRecordData')

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
            'schema=%r'
            'config=%r)'
            ) % (
               self.sru_version,
               self.server,
               self.database,
               self.index,
               self.schema,
               self.config,
            )

    def _parse_content(self, xml):
        self._check_response_tag(xml, 'explainResponse')

        record_schema = self.xmlparser.find(xml, './/sru:recordSchema').text
        if record_schema:
            self.xmlparser.namespaces['zr'] = record_schema

        self.sru_version = self.xmlparser.find(xml, './sru:version').text

        self.server = self._parse_server(xml)
        self.database = self._parse_database(xml)
        self.index = self._parse_index(xml)
        self.schema = self._parse_schema(xml)
        self.config = self._parse_config(xml)

    def _parse_server(self, xml):
        server_info = {
            'host': self.xmlparser.find(xml, './/zr:serverInfo/zr:host').text,
            'port': self.xmlparser.find(xml, './/zr:serverInfo/zr:port').text,
        }
        server_info['port'] = self.maybe_int(server_info['port'])
        return server_info

    def _parse_schema(self, xml):
        def bool_or_none(v):
            if v is None:
                return None
            return bool(v)

        def ident(a):
            return a

        attributes = {
            'identifier': ident,
            'name': ident,
            'location': ident,
            'sort': bool_or_none,
            'retrieve': bool_or_none,
        }

        schemas = {}
        for schema in self.xmlparser.findall(xml, './/zr:schemaInfo/zr:schema'):
            schema_info = {}
            for attr, fn in attributes.items():
                xml_attr = schema.attrib.get(attr)
                if xml_attr:
                    schema_info[attr] = fn(xml_attr)
            schema_info['title'] = self.xmlparser.find(schema, './zr:title').text
            schemas[schema.attrib.get('name')] = schema_info
        return schemas

    def _parse_config(self, xml):
        config = {}
        for setting in self.xmlparser.findall(xml, './/zr:configInfo/zr:setting'):
            t = setting.attrib['type']
            config[t] = self.maybe_int(setting.text)

        # defaults
        defaults = {}
        for default in self.xmlparser.findall(xml, './/zr:configInfo/zr:default'):
            t = default.attrib['type']
            defaults[t] = self.maybe_int(default.text)
        config['defaults'] = defaults
        return config

    def _parse_database(self, xml):
        db = self.xmlparser.find(xml, './/zr:databaseInfo')
        db_info = {
            'title': self.xmlparser.find(db, ['./zr:title', './title']).text,
            'description': self.xmlparser.find(db, ['./zr:description', './description']).text,
            'contact': self.xmlparser.find(db, ['./zr:contact', './contact']).text,
        }
        db_info = {k: v.strip() if v else v for (k, v) in db_info.items()}
        return db_info

    def _parse_index(self, xml):
        index = defaultdict(defaultdict)
        for index_set in self.xmlparser.findall(xml, './/zr:indexInfo/zr:set'):
            index[index_set.attrib['name']] = defaultdict()

        for index_field in self.xmlparser.findall(xml, './/zr:indexInfo/zr:index'):
            title = self.xmlparser.find(index_field, './zr:title').text or \
                    self.xmlparser.find(index_field, './title').text
            if title:
                title = title.strip()
            for name in self.xmlparser.findall(index_field, './/zr:map/zr:name'):
                index[name.attrib['set']][name.text.strip()] = title

        return {k: dict(v) for k, v in dict(index).items()}
