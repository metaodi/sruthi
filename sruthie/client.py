# -*- coding: utf-8 -*-

import requests
from . import errors
from defusedxml.ElementTree import parse

class Client:
    OPERATIONS = {
        'searchretrieve': {
            'response': 'searchRetrieveResponse'
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
            raise errors.SruthieError("HTTP error: %s" % e)
        except requests.exceptions.RequestException as e:
            raise errors.SruthieError("Request error: %s" % e)
        return self._parse_xml(res.content)

    def _parse_xml(self, content):
        # handle exceptions and check if an error occued (diagnostic, Unsupported version etc.)
        xml = parse(content)
        return xml
        
    def searchretrieve(self, query):
        params = {
            'operation': 'searchretrieve',
            'version': '1.2',
            'query': query,
        }
        content = self._get_content(self.url, params)
        # try/except for XML parsing error
        try:
            xml = parse(content)
        except Exception as e:
            raise errors.SruError("Error while parsing XML: %s" % e)

        self._check_errors(xml, 'searchretriee')

        return xml

    def _check_errors(xml, operation):
        config = self.OPERATIONS[operation]
        if not xml.find('./%s' % config['response']):
            raise errors.ServerIncompatibleError('Server response did not contain a searchRetrieveResponse tag')

        diagnostics = xml.find('/searchRetrieveResponse/diagnostics/diagnostic')
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
