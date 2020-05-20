import mock
import unittest
import os

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


class SruthiTestCase(unittest.TestCase):
    def _session_mock(self, session_mock, filename=None):
        if not filename:
            filename = self._testMethodName + ".xml"
        path = os.path.join(
            __location__,
            'fixtures',
            filename
        )
        with open(path) as file:
            session_mock.return_value.get.return_value = mock.MagicMock(content=file.read())

