# -*- coding: utf-8 -*-

from . import client


def searchretrieve(url, query, operation='searchretrieve'):
    c = client.Client(url)
    return c.searchretrieve(query, operation=operation)


def explain(url):
    c = client.Client(url)
    return c.explain()
