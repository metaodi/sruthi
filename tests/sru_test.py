from sruthi_test import SruthiTestCase
import sruthi


class TestSru(SruthiTestCase):
    def test_searchretrieve(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query')
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)

    def test_explain(self):
        info = sruthi.explain('http://test.com/sru/')
        self.assertIsInstance(info, sruthi.response.ExplainResponse)
