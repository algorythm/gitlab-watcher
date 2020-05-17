import requests
from requests.models import Response

class Http:
    def __init__(self, base: str):
        self.base = base.strip('/')
        self.headers = {}

    def add_header(self, key: str, value: str):
        self.headers[key] = value

    def get(self, url) -> Response:
        return requests.get(f'{self.base}/{url}', headers=self.headers)