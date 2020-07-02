import requests
from requests.models import Response
from src.common.logging_helper import get_logger

class Http:
    def __init__(self, base: str):
        self.logger = get_logger(__name__)
        self.base = base.strip('/')
        self.headers = {}

    def add_header(self, key: str, value: str):
        self.headers[key] = value

    def get(self, url: str) -> Response:
        response = requests.get(f'{self.base}/{url.lstrip("/")}', headers=self.headers)
        self.parse_errors(url, response)
        return response

    def put_json(self, url: str, body, logging: bool = True) -> Response:
        if logging:
            self.logger.info(f'putting {self.base}/{url.lstrip("/")}')
        response = requests.put(f'{self.base}/{url.lstrip("/")}', headers=self.headers, json=body)

        if logging:
            self.parse_errors(url, response)

        return response

    def post_json(self, url: str, body, logging: bool = True) -> Response:
        if logging:
            self.logger.info(f'posting {self.base}/{url.lstrip("/")}')
        headers = self.headers
        response = requests.post(f'{self.base}/{url.lstrip("/")}', headers=headers, json=body)

        if logging:
            self.parse_errors(url, response)
        return response

    def parse_errors(self, url: str, response: Response):
        if response.status_code < 300:
            return

        error_message = ''
        if 'Content-Type' in response.headers and response.headers['Content-Type'] == 'application/json':
            body = response.json()
            if 'message' in body:
                error_message = body['message']
            elif 'error' in body:
                error_message = body['error']
            elif 'errorMessage' in body:
                body['error_message']
            elif 'error_message' in body:
                error_message = body['error_message']
            else:
                error_message = response.text
        else:
            error_message = response.text

        if response.status_code == 404:
            self.logger.warning(f"{url}: resource doesn't exist")
        else:
            self.logger.error(f'{url} failed request ({response.status_code}): {error_message}')
            raise Exception(error_message)
