# -*- coding: utf-8 -*-

import requests

class Client:
    def __init__(self, url=None):
        self.session = requests.Session()
        self.url = url
        
    def search(self, query):
        pass
    
    def explain(self):
        pass