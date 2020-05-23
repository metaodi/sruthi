# -*- coding: utf-8 -*-

import requests
from . import errors
from . import xmlparse
from . import metadata


class Client(object):
    def __init__(self, url=None, page_size=100):
        self.session = requests.Session()
        self.url = url
        # get explain here to get supported version?
        # get number_of_records from explain as well

    def searchretrieve(self, query):
        params = {
            'operation': 'searchretrieve',
            'version': '1.2',
            'query': query,
            'startRecord': 1
        }
        data_loader = SruDataLoader(self.url, params, 'searchretrieve')
        result = data_loader()

        data = metadata.SruData(
            records=result['records'],
            sru_version=result['sru_version'],
            count=result['count'],
            data_loader=data_loader
        )
        return data

    def explain(self):
        params = {
            'operation': 'explain',
            'version': '1.2',
        }
        content = self._get_content(self.url, params)
        return content


class SruDataLoader(object):
    sru = '{http://www.loc.gov/zing/srw/}'
    OPERATIONS = {
        'searchretrieve': {
            'response': '%ssearchRetrieveResponse' % sru,
        },
        'explain': {
            'response': 'sru:explainResponse',
        },
    }

    def __init__(self, url, params, operation):
        self.session = requests.Session()
        self.url = url
        self.params = params
        self.operation = operation
        self.next_start_record = 1

    def __call__(self, **kwargs):
        self.params.update(kwargs)
        if self.next_start_record is None:
            raise errors.NoMoreRecordsError()
        self.params['startRecord'] = self.next_start_record
        xml = self._get_content(self.url, self.params)
        self._check_errors(xml)

        sru_version = xmlparse.find(xml, './sru:version').text
        count = int(xmlparse.find(xml, './sru:numberOfRecords').text)
        records = metadata.extract_records(xml)

        next_start_record = xmlparse.find(xml, './sru:nextRecordPosition').text
        if next_start_record:
            self.next_start_record = int(next_start_record)
        else:
            self.next_start_record = None

        return {
            'xml': xml,
            'sru_version': sru_version,
            'count': count,
            'records': records,
            'next_start_record': self.next_start_record,
        }

    def _get_content(self, url, params):
        try:
            res = self.session.get(
                url,
                params=params
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.SruthiError("HTTP error: %s" % e)
        except requests.exceptions.RequestException as e:
            raise errors.SruthiError("Request error: %s" % e)

        return xmlparse.parse(res.content)

    def _check_errors(self, xml):
        config = self.OPERATIONS[self.operation]
        if not xml.tag == config['response']:
            raise errors.ServerIncompatibleError(
                'Server response did not contain a searchRetrieveResponse tag'
            )

        diagnostics = xmlparse.find(
            xml,
            f'{self.sru}diagnostics/{self.sru}diagnostic'
        )
        if diagnostics:
            error_msg = " ".join([d.find('detail').text for d in diagnostics])
            raise errors.SruError(error_msg)
