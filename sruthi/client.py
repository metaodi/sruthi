# -*- coding: utf-8 -*-

import requests
from . import errors
from . import xmlparse
from . import response


class Client(object):
    def __init__(self, url=None, maximum_records=10, record_schema=None):
        self.url = url
        self.maximum_records = maximum_records
        self.sru_version = '1.2'
        self.record_schema = record_schema

    def searchretrieve(self, query, start_record=1, requests_kwargs=None):
        params = {
            'operation': 'searchRetrieve',
            'version': self.sru_version,
            'query': query,
            'startRecord': start_record,
            'maximumRecords': self.maximum_records,
        }

        if self.record_schema:
            params['recordSchema'] = self.record_schema

        data_loader = DataLoader(self.url, params, requests_kwargs)
        return response.SearchRetrieveResponse(data_loader)

    def explain(self, requests_kwargs=None):
        params = {
            'operation': 'explain',
            'version': self.sru_version,
        }
        data_loader = DataLoader(self.url, params, requests_kwargs)
        return response.ExplainResponse(data_loader)


class DataLoader(object):
    def __init__(self, url, params, requests_kwargs=None):
        self.session = requests.Session()
        self.url = url
        self.params = params
        self.response = None
        self.xmlparser = xmlparse.XMLParser()
        self.requests_kwargs = requests_kwargs or {}

    def load(self, **kwargs):
        self.params.update(kwargs)
        xml = self._get_content(self.url, self.params)
        self._check_errors(xml)
        return xml

    def _get_content(self, url, params):
        try:
            res = self.session.get(
                url,
                params=params,
                **self.requests_kwargs
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.SruthiError("HTTP error: %s" % e)
        except requests.exceptions.RequestException as e:
            raise errors.SruthiError("Request error: %s" % e)

        return self.xmlparser.parse(res.content)

    def _check_errors(self, xml):
        sru = '{http://www.loc.gov/zing/srw/}'
        diag = '{http://www.loc.gov/zing/srw/diagnostic/}'
        diagnostics = self.xmlparser.find(
            xml,
            f'{sru}diagnostics/{diag}diagnostic'
        )
        if diagnostics:
            error_msg = ", ".join([d.text for d in diagnostics])
            raise errors.SruError(error_msg)
