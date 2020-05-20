import mock
from sruthi_tests import SruthiTestCase
from sruthi.client import Client


class TestSruthiClient(SruthiTestCase):
    @mock.patch('sruthi.client.requests.Session')
    def test_searchretrieve(self, session_mock):
        # mock session
        self._session_mock(session_mock)

        client = Client('http://test.com/sru')

        r = client.searchretrieve('Test-Query')
        self.assertEquals(r.count, 12)
        self.assertEquals(len(r.records), 12)

        for rec in r:
            self.assertIsInstance(rec, dict)
            self.assertEquals(rec['schema'], 'isad')
        
        session_mock.return_value.get.assert_any_call('http://test.com/sru', params={'startRecord': 1, 'query': 'Test-Query', 'operation': 'searchretrieve', 'version': '1.2'})

