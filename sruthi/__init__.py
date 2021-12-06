__version__ = '1.0.0'
__all__ = ['client', 'errors', 'response', 'xmlparse']

from .errors import SruthiError, ServerIncompatibleError, SruError, NoMoreRecordsError  # noqa
from .errors import SruthiWarning, WrongNamespaceWarning # noqa
from .client import Client # noqa


def searchretrieve(url, query, **kwargs):
    search_params = ['query', 'start_record', 'requests_kwargs']
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs['query'] = query

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs['url'] = url

    c = Client(**client_kwargs)
    return c.searchretrieve(**search_kwargs)


def explain(url, **kwargs):
    c = Client(url, **kwargs)
    return c.explain()
