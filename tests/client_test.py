from sruthi_test import SruthiTestCase
from sruthi.client import Client
from sruthi.errors import WrongNamespaceWarning


class TestSruthiClient(SruthiTestCase):
    def test_searchretrieve(self):
        client = Client('http://test.com/sru')
        r = client.searchretrieve('Test-Query')
        self.assertEqual(r.count, 12)
        self.assertEqual(len(r.records), 12)

        self.assertEqual(
            r[0],
            {
                'reference': 'VII.335.:2.34.8.',
                'extra': {
                    'score': '0.38',
                    'link': 'https://amsquery.stadt-zuerich.ch/detail.aspx?Id=410130',  # noqa
                    'hasDigitizedItems': '0',
                    'endDateISO': '1998-12-31',
                    'beginDateISO': '1998-01-01',
                    'beginApprox': '0',
                    'endApprox': '0'
                },
                'descriptionlevel': 'Dossier',
                'title': u'Podium "Frauen und Politik" beim Jubil\xe4umsanlass "Frauenrechte-Menschenrechte" des Bundes Schweizerischer Frauenorganisationen BSF zu 150 Jahre Bundesstaat, 50 Jahre UNO-Menschenrechtserkl\xe4rung und 27 Jahre politische Gleichberechtigung im Nationalratssaal in Bern vom 4. April 1998',  # noqa
                'extent': None,
                'date': '1998',
                'creator': None,
                'schema': 'isad',
            }
        )

    def test_searchretrieve_warning(self):
        with self.assertWarns(WrongNamespaceWarning):
            client = Client('http://server-with-wrong-sru.namespace/sru/search')
            r = client.searchretrieve('dc.title = Test')
            self.assertEqual(r.count, 10)

    def test_searchretrieve_slice(self):
        client = Client('http://test.com/sru/search')
        r = client.searchretrieve('dc.title = Zürich')
        self.assertEqual(r.count, 10)
        self.assertEqual(len(r.records), 10)

        # access by index
        self.assertEqual(r[0]['id'], '107853744')
        self.assertEqual(r[3]['id'], '10723971X')
        self.assertEqual(r[-1]['id'], '113008686')
        with self.assertRaises(IndexError):
            print(r[-200])

        # slicing
        res = list(r[:5])
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0]['id'], '107853744')
        self.assertEqual(res[1]['id'], '105427527')
        self.assertEqual(res[2]['id'], '106876457')
        self.assertEqual(res[3]['id'], '10723971X')
        self.assertEqual(res[4]['id'], '108757544')

        res = list(r[8:])
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['id'], '07865257X')
        self.assertEqual(res[1]['id'], '113008686')

        res = list(r[3:10:3])
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]['id'], '10723971X')
        self.assertEqual(res[1]['id'], '075640988')
        self.assertEqual(res[2]['id'], '113008686')

    def test_explain(self):
        client = Client('https://test.com/sru')
        info = client.explain()

        # server
        server = info.server
        self.assertEqual(server['host'], 'https://test.com/sru')
        self.assertEqual(server['port'], 80)

        # database
        db = info.database
        self.assertEqual(db['title'], 'Testarchiv Online Search')
        self.assertEqual(db['description'], 'Durchsuchen der Bestände des Testarchivs.')
        self.assertEqual(db['contact'], 'test@test.com')

        # index
        index = info.index
        self.assertEqual(len(index), 1)
        self.assertEqual(list(index.keys()), ['isad'])
        self.assertIn('title', index['isad'])
        self.assertIn('reference', index['isad'])
        self.assertIn('date', index['isad'])
        self.assertIn('descriptionlevel', index['isad'])
        self.assertEqual(index['isad']['reference'], 'Reference Code')

        # schema
        schema = info.schema
        self.assertEqual(len(schema), 1)
        self.assertEqual(list(schema.keys()), ['isad'])
        self.assertEqual(schema['isad']['name'], 'isad')
        self.assertEqual(schema['isad']['title'], 'ISAD(G)')

        # config
        config = info.config
        print(config)
        self.assertEqual(config['maximumRecords'], 99)
        self.assertEqual(config['my-test-config'], 'test123')
        self.assertEqual(config['defaults']['numberOfRecords'], 99)

    def test_passing_maximum_records(self):
        client = Client('http://my-param.com/sru', maximum_records=111)
        self.assertEqual(client.maximum_records, 111)

        client.searchretrieve('test-query')
        self.session_mock.return_value.get.assert_called_once_with(
            'http://my-param.com/sru',
            params={
                'operation': 'searchretrieve',
                'version': '1.2',
                'query': 'test-query',
                'startRecord': 1,
                'maximumRecords': 111,
            }
        )

    def test_passing_record_schema(self):
        client = Client('http://my-param.com/sru', record_schema='dc')
        self.assertEqual(client.record_schema, 'dc')

        client.searchretrieve('test-query')
        self.session_mock.return_value.get.assert_called_once_with(
            'http://my-param.com/sru',
            params={
                'operation': 'searchretrieve',
                'version': '1.2',
                'query': 'test-query',
                'startRecord': 1,
                'recordSchema': 'dc',
                'maximumRecords': 10,
            }
        )

    def test_passing_start_record(self):
        client = Client('http://my-param.com/sru')

        client.searchretrieve('test-query', start_record=10)
        self.session_mock.return_value.get.assert_called_once_with(
            'http://my-param.com/sru',
            params={
                'operation': 'searchretrieve',
                'version': '1.2',
                'query': 'test-query',
                'startRecord': 10,
                'maximumRecords': 10,
            }
        )
