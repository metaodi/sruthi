from sruthi_test import SruthiTestCase
import sruthi


class TestSru(SruthiTestCase):
    def test_searchretrieve(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query')
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)

    def test_searchretrieve_with_maximum_records(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', maximum_records=100)
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)

    def test_searchretrieve_with_record_schema(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', record_schema='isad')
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)

    def test_searchretrieve_with_start_record(self):
        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query', start_record=10)
        self.assertIsInstance(r, sruthi.response.SearchRetrieveResponse)

    def test_explain(self):
        info = sruthi.explain('http://test.com/sru/')
        self.assertIsInstance(info, sruthi.response.ExplainResponse)

    def test_client(self):
        client = sruthi.Client('http://test.com/sru')
        self.assertIsInstance(client, sruthi.client.Client)
