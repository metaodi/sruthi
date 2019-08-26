# -*- coding: utf-8 -*-

from . import client

def search(url, query):
    c = client.Client(url)
    return c.search(query)

def explain(url):
    c = client.Client(url)
    return c.explain()