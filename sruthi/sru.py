# -*- coding: utf-8 -*-

from . import client


def searchretrieve(url, query, **kwargs):
    search_params = ['query', 'start_record', 'requests_kwargs']
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs['query'] = query

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs['url'] = url

    c = client.Client(**client_kwargs)
    return c.searchretrieve(**search_kwargs)


def explain(url):
    c = client.Client(url)
    return c.explain()
