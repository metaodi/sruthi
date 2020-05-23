# -*- coding: utf-8 -*-

from . import client


def searchretrieve(url, query):
    c = client.Client(url)
    return c.searchretrieve(query)


def explain(url):
    c = client.Client(url)
    return c.explain()
