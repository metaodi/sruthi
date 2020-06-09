# make sure you have termcolor and yaml installed: pip install termcolor pyyaml
import sruthi
from termcolor import cprint
import yaml

sru_endpoints = [
    'https://suche.staatsarchiv.djiktzh.ch/SRU/',
    'https://amsquery.stadt-zuerich.ch/SRU/',
    'http://lx2.loc.gov:210/LCDB?',
    'https://sru.swissbib.ch/sru/explain',
]


def print_header(s):
    cprint(s, 'green', attrs=['bold'])


def print_title(s):
    cprint(s, attrs=['bold'])


def dump(d):
    print(yaml.dump(d, allow_unicode=True, default_flow_style=False))


for endpoint in sru_endpoints:
    print_header(20 * '=')
    print_header('=')
    print_header(f'= {endpoint}')
    print_header('=')
    print_header(20 * '=')
    info = sruthi.explain(endpoint)

    print_title('Server:')
    dump(info.server)
    print('')

    print_title('Database:')
    dump(info.database)
    print('')

    print_title('Index:')
    dump(info.index)
    print('')

    print_title('Schema:')
    dump(info.schema)
    print('')

    print_title('Config:')
    dump(info.config)
    print('')

    print('')
    print('')
