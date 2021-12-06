from sruthi_test import SruthiTestCase
import sruthi


class TestSru(SruthiTestCase):
    def test_searchretrieve(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query')
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': 'Test-Query',
                'startRecord': 1,
                'maximumRecords': 10,
            }
        )

    def test_searchretrieve_with_maximum_records(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', maximum_records=100)
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': 'Test-Query',
                'startRecord': 1,
                'maximumRecords': 100,
            }
        )

    def test_searchretrieve_with_record_schema(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', record_schema='isad')
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': 'Test-Query',
                'startRecord': 1,
                'maximumRecords': 10,
                'recordSchema': 'isad',
            }
        )

    def test_searchretrieve_with_start_record(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', start_record=10)
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': 'Test-Query',
                'startRecord': 10,
                'maximumRecords': 10,
            }
        )

    def test_searchretrieve_with_requests_kwargs(self):
        r = sruthi.searchretrieve(
            'http://test.com/sru/',
            'Test-Query',
            requests_kwargs={'verify': False}
        )
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': 'Test-Query',
                'startRecord': 1,
                'maximumRecords': 10,
            },
            verify=False
        )

    def test_explain(self):
        info = sruthi.explain('http://test.com/sru/')
        self.assertEqual(info.sru_version, '1.2'),
        self.assertEqual(info['sru_version'], '1.2')
        self.assertIsInstance(info, sruthi.response.AttributeDict)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://test.com/sru/',
            params={
                'operation': 'explain',
                'version': '1.2',
            }
        )

    def test_client(self):
        client = sruthi.Client('http://test.com/sru')
        self.assertIsInstance(client, sruthi.client.Client)
