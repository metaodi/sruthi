# -*- coding: utf-8 -*-

import requests
from . import errors
from . import xmlparse
from . import metadata

class Client:
    sru = '{http://www.loc.gov/zing/srw/}'
    OPERATIONS = {
        'searchretrieve': {
            'response': '%ssearchRetrieveResponse' % sru,
        },
        'explain': {
            'response': 'sru:eplainResponse',
        },
    }

    def __init__(self, url=None):
        self.session = requests.Session()
        self.url = url
        # get explain here to get supported version?

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

    def searchretrieve(self, query):
        params = {
            'operation': 'searchretrieve',
            'version': '1.2',
            'query': query,
        }
        xml = self._get_content(self.url, params)
        self._check_errors(xml, 'searchretrieve')

        records = metadata.extract_records(xml)
        return records

    def _check_errors(self, xml, operation):
        config = self.OPERATIONS[operation]
        if not xml.tag == config['response']:
            raise errors.ServerIncompatibleError('Server response did not contain a searchRetrieveResponse tag')

        diagnostics = xmlparse.find(xml, '%sdiagnostics/%sdiagnostic' % (self.sru, self.sru))
        if diagnostics:
           error_msg = " ".join([d.find(detail).text for d in diagnostics])
           raise errors.SruError(error_msg)
    
    def explain(self):
        params = {
            'operation': 'explain',
            'version': '1.2',
            'query': query,
        }
        content = self._get_content(self.url, params)
        return content
