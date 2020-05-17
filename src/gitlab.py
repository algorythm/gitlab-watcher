from __future__ import annotations
from src.http_helper import Http

class GitLab:
    def __init__(self, project_id: str, token: str, base = 'https://gitlab.com/api/v4'):
        self.project_id = project_id
        self.token = token
        self.http = Http(base)

        self.http.add_header('Private-Token', token)

    def list_users(self):
        req = self.http.get(f'/projects/{self.project_id}/pipelines/')

        print(req.status_code)
        print(req.text)

    def latest_tag(self) -> Tag:
        resp = self.http.get(f'/projects/{self.project_id}/repository/tags')
        tags = resp.json()

        latest_tag = tags[0]

        return Tag(latest_tag['name'], latest_tag['message'])

    def pipeline_status_for_tag(self, tag: str) -> str:
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
