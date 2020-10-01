# -*- coding: utf-8 -*-

from . import client


def searchretrieve(url, query, operation='searchretrieve', recordSchema=None):
    c = client.Client(url)
    if recordSchema:
        return c.searchretrieve(query, operation=operation, recordSchema=recordSchema)
    else:
        return c.searchretrieve(query, operation=operation)


def explain(url):
    c = client.Client(url)
    return c.explain()
