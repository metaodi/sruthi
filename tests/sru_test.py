import mock
from sruthi_test import SruthiTestCase
import sruthi


class TestSruthiClient(SruthiTestCase):

    @mock.patch('sruthi.client.requests.Session')
    def test_searchretrieve(self, session_mock):
        # mock session
        self._session_mock(session_mock)

        r = sruthi.searchretrieve('http://test.com/sru/', 'Test-Query')
        self.assertEqual(r.count, 12)
        self.assertEqual(len(r.records), 12)

        print(r[0])
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
