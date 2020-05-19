from __future__ import annotations
from src.http_helper import Http
from src.common.logging_helper import get_logger

class GitLab:
    def __init__(self, project_id: str, token: str, base = 'https://gitlab.com/api/v4'):
        self.project_id = project_id
        self.token = token
        self.http = Http(base)

        self.logger = get_logger(__name__)

        self.http.add_header('Private-Token', token)

    def get_user(self):
        self.logger.debug('fetching GitLab user information')
        req = self.http.get(f'/user/')

        return req.json()

    def latest_tag(self) -> Tag:
        self.logger.debug('fetching all tags from GitLab')
        resp = self.http.get(f'/projects/{self.project_id}/repository/tags')
        tags = resp.json()

        latest_tag = tags[0]

        return Tag(latest_tag['name'], latest_tag['message'])

    def pipeline_status_for_tag(self, tag: str) -> str:
        self.logger.debug(f'looking for ci-job for "{tag}"')
        resp = self.http.get(f'/projects/{self.project_id}/pipelines?ref={tag}')

        if resp.status_code == 404:
            return None

        result = resp.json()

        if len(result) == 0:
            return None

        return result[0]['status']

class Tag:
    def __init__(self, name, message):
        self.name = name
        self.message = message
