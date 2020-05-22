from src.config import ConfigReader, GitLabConfig
from src.gitlab import GitLab
from datetime import datetime
import time

from src.common.logging_helper import get_logger
from src.watcher_job import GitLabWatcher

from pync import Notifier
import re

# nice rumps example: https://camillovisini.com/create-macos-menu-bar-app-pomodoro/
# send notification with view button: https://g3rv4.com/2015/08/macos-notifications-python-pycharm

def main(config: GitLabConfig):
    logger = get_logger(__name__)

    gl = GitLab(config.project_id, config.token)

    user = gl.get_user()
    logger.info(f'Welcome {user["name"]} ({user["username"]})')

    latest_tag = gl.latest_tag()
    ci_status = gl.pipeline_status_for_tag(latest_tag.name)

    if ci_status != None:
        logger.info(f'tag: {latest_tag.name}::{ci_status.status} ({ci_status.completed_jobs} / {ci_status.job_count} -- {ci_status.pending_jobs} pending)')

    GitLabWatcher(gl, user['username']).run()

if __name__ == '__main__':
    config = ConfigReader().read_config()
    main(config.gitlab_config)
