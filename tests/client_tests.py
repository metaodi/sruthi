import mock
import unittest
import os

import sruthi

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


class TestSruthiClient(unittest.TestCase):
    def _session_mock(self, session_mock, filename=None):
        if not filename:
            filename = self._testMethodName + ".xml"
        path = os.path.join(
            __location__,
            'fixtures',
            filename
        )
        with open(path) as file:
            session_mock.return_value = mock.MagicMock(
                get=mock.MagicMock(
                    return_value=mock.MagicMock(content=file.read())
                )
            )

    @mock.patch('sruthi.client.requests.Session')
    def test_searchretrieve(self, session_mock):
        # mock session
        self._session_mock(session_mock)

        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query')
        self.assertEquals(r.count, 12)
        self.assertEquals(len(r.records), 12)

        for rec in r:
            self.assertIsInstance(rec, dict)
            self.assertEquals(rec['schema'], 'isad')


