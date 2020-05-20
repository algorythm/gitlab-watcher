from src.gitlab import GitLab
from src.common.logging_helper import get_logger
import rumps
from threading import Thread
import time
from pync import Notifier

class GitLabWatcher():
    def __init__(self, gitlab: GitLab, username: str):
        self.gitlab = gitlab
        self.logger = get_logger(__name__)
        self.app = None

        self.ci_status = ''
        # rumps.notification('test', 'sub', 'my message', action_button='View', sound=True, data={'action': 'open_url', 'value': 'https://google.com'})

    def fetch_status(self):
        latest_tag = self.gitlab.latest_tag()
        ci = self.gitlab.pipeline_status_for_tag(latest_tag.name)

        return latest_tag.name, ci

    def heartbeat(self):
        while True:
            tag, ci = self.fetch_status()
            if self.app == None:
                time.sleep(1)
                continue

            if self.ci_status == 'running' and ci.status == 'running':
                tag_url = f'https://gitlab.com/consensusaps/connect/-/tags/{tag}'
                rumps.notification('Build Completed', f'Completed build for {tag}', f'Docker build for {tag} has not completed', sound=True)
                Notifier.notify(f'Docker build for {tag} has not completed', title=f'Completed build for {tag}', open=tag_url)

            if ci.status == 'success':
                self.app.title = f't: {tag}'
            elif ci.status == 'running':
                self.logger.info(f'building {tag} -- {ci.completed_jobs} / {ci.job_count} -- {ci.pending_jobs} pending')
                self.app.title = f'👷🏼‍♀️ {tag} ({ci.completed_jobs} / {ci.job_count})[{ci.pending_jobs}]'
            elif ci.status == 'pending':
                self.app.title = f'🍿 {tag}'
            else:
                self.app.title = f'☔️ {tag}'
                self.logger.info(f'ci status for {tag}: {ci}')
            time.sleep(20)

    def run(self):
        tag, _ = self.fetch_status()
        self.logger.debug('starting heartbeat thread')
        Thread(target=self.heartbeat).start()
        self.logger.debug('starting rumps app')
        self.app = rumps.App(f't: {tag}')
        self.app.run()

