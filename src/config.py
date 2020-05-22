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

        return WatcherConfig(GitLabConfig(config), SlackConfig(config))

if __name__ == '__main__':
    ConfigReader().get_env()

class GitLabConfig:
    def __init__(self, config: dict):
        gitlab_config = config['gitlab']

        self.token = gitlab_config['token']
        self.project_id = gitlab_config['project_id']
        self.base = gitlab_config['base']
        self.repository = gitlab_config['repository']

class SlackConfig:
    def __init__(self, config: dict):
        if 'slack' not in config:
            self.configured = False
            return
        slack_config = config['slack']

        self.token = slack_config['token']
        self.ci_done_channel = slack_config['channel']['ci_done']
        self.changelog_channel = slack_config['channel']['changelog']

        self.configured = True

class WatcherConfig:
    def __init__(self, gitlab_config: GitLabConfig, slack_config: SlackConfig):
        self.gitlab_config = gitlab_config
        self.slack_config = slack_config
