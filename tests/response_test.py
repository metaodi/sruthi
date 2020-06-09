import mock
from sruthi_test import SruthiTestCase
from sruthi.response import SearchRetrieveResponse, ExplainResponse
from sruthi import xmlparse
import os

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


class TestSearchRetrieveResponse(SruthiTestCase):
    def _data_loader_mock(self, filenames):
        xmls = []
        for filename in filenames:
            xmls.append(self._load_xml(filename))
        m = mock.Mock()
        m.load.side_effect = xmls
        return m

    def _load_xml(self, filename):
        path = os.path.join(
            __location__,
            'fixtures',
            filename
        )
        xmlparser = xmlparse.XMLParser()
        with open(path) as file:
            content = file.read()
        return xmlparser.parse(content)


    def test_response_single(self):
        data_loader = self._data_loader_mock(['response_single.xml'])
        res = SearchRetrieveResponse(data_loader)

        self.assertEqual(res.count, 1)
        self.assertEqual(res.__length_hint__(), 1)
        self.assertEqual(res.sru_version, '1.2')
        self.assertIsNone(res.next_start_record)

    def test_response_multi(self):
        data_loader = self._data_loader_mock(['response_multiple_1.xml'])
        res = SearchRetrieveResponse(data_loader)

        self.assertEqual(res.count, 220)
        self.assertEqual(res.__length_hint__(), 220)
        self.assertEqual(res.sru_version, '1.2')
        self.assertEqual(res.next_start_record, 100)

    def test_response_iterator(self):
        filenames = [
            'response_multiple_1.xml',
            'response_multiple_2.xml',
            'response_multiple_3.xml',
        ]
        data_loader = self._data_loader_mock(filenames)
        res = SearchRetrieveResponse(data_loader)

        next_res = next(iter(res))
        self.assertIsNotNone(next_res)
        self.assertIsInstance(next_res, dict)
        self.assertEqual(next_res['schema'], 'isad')
        self.assertEqual(next_res['reference'], 'Z 248.24')

        records = [r for r in res]
        self.assertEqual(len(records), 220)
        self.assertEqual(data_loader.load.call_count, 3)

    def test_response_index(self):
        filenames = [
            'response_multiple_1.xml',
            'response_multiple_2.xml',
            'response_multiple_3.xml',
        ]
        data_loader = self._data_loader_mock(filenames)
        res = SearchRetrieveResponse(data_loader)
        self.assertEqual(data_loader.load.call_count, 1)

        self.assertIsNotNone(res[150])
        self.assertIsInstance(res[150], dict)
        self.assertEqual(data_loader.load.call_count, 2)

        self.assertIsNotNone(res[205])
        self.assertIsInstance(res[205], dict)
        self.assertEqual(data_loader.load.call_count, 3)
        