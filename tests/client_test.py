import mock
from sruthi_test import SruthiTestCase
from sruthi.client import Client


class TestSruthiClient(SruthiTestCase):
    @mock.patch('sruthi.client.requests.Session')
    def test_searchretrieve(self, session_mock):
        # mock session
        self._session_mock(session_mock)

        client = Client('http://test.com/sru')

        r = client.searchretrieve('Test-Query')
        self.assertEqual(r.count, 12)
        self.assertEqual(len(r.records), 12)

        for rec in r:
            self.assertIsInstance(rec, dict)
            self.assertEqual(rec['schema'], 'isad')

        session_mock.return_value.get.assert_any_call(
            'http://test.com/sru',
            params={
                'startRecord': 1,
                'query': 'Test-Query',
                'operation': 'searchretrieve',
                'version': '1.2'
            }
        )

# add test for getitem with slices etc.
# print("-3")
# print(records[-3])
# print("1")
# print(records[1])
# print("2:20:2")
# print(records[2:20:2])
# print(":2")
# print(records[:2])
# print("159")
# print(records[159])
# print("5:1")
# print(records[5::-1])
