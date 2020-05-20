from __future__ import annotations
import os
import yaml

class ConfigReader:
    def __init__(self, config_path: str = 'env.yml'):
        self.config_path = config_path

    def get_env(self):
        if not os.path.isfile(self.config_path):
            raise Exception(f'"{self.config_path}" doesn\'t exist')

        with open(self.config_path) as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def read_config(self) -> WatcherConfig:
        config = self.get_env()

        return WatcherConfig(GitLabConfig(config['gitlab']), SlackConfig(config['slack']))

if __name__ == '__main__':
    ConfigReader().get_env()

class GitLabConfig:
    def __init__(self, config: dict):
        self.token = config['token']
        self.project_id = config['project_id']
        self.base = config['base']
        self.repository = config['repository']

class SlackConfig:
    def __init__(self, config: dict):
        self.token = config['token']
        self.ci_done_channel = config['channel']['ci_done']
        self.changelog_channel = config['channel']['changelog']

class WatcherConfig:
    def __init__(self, gitlab_config: GitLabConfig, slack_config: SlackConfig):
        self.gitlab_config = gitlab_config
        self.slack_config = slack_config
