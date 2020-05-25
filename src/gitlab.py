from __future__ import annotations
from src.common.http_helper import Http
from src.common.logging_helper import get_logger

from progressbar import ProgressBar
import progressbar
import time

class GitLab:
    def __init__(self, project_id: str, token: str, base = 'https://gitlab.com/api/v4'):
        self.project_id = project_id
        self.token = token
        self.http = Http(base)

        progressbar.streams.wrap_stdout()
        progressbar.streams.wrap_stderr()
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

    def get_tag(self, tag: str) -> Tag:
        self.logger.debug(f'fetching tag {tag} from GitLab')
        resp = self.http.get(f'/projects/{self.project_id}/repository/tags/{tag}')

        if resp.status_code == 404:
            self.logger.warning(f"couldn't find tag {tag}")
            return None

        result = resp.json()
        return Tag(result['name'], result['message'])

    def get_merge_request(self, mr_id: int, logging: bool = True):
        if logging:
            self.logger.debug(f'fetching mr {mr_id} from GitLab')
        resp = self.http.get(f'/projects/{self.project_id}/merge_requests/{mr_id}')

        if resp.status_code == 404:
            return None

        return resp.json()

    def set_mr_label(self, mr_id: str, label: str, logging: bool = True):
        if logging:
            self.logger.debug(f'setting label "{label}" for MR !{mr_id}')

        resp = self.http.put_json(f'/projects/{self.project_id}/merge_requests/{mr_id}', {'add_labels': label})

        if resp.status_code == 404:
            return None

        return resp.json()

    def change_mr_labels(self, *mrs):
        merge_requests = []
        updated_merge_requests = 0

        bar = ProgressBar(max_value=len(mrs[0]), redirect_stdout=True, redirect_stderr=True)

        for i, mr in enumerate(mrs[0]):
            self.logger.info(f'Handling MR !{mr}')
            fetched_mr = self.get_merge_request(mr, True)

            # Get phase status for MR
            phase_label = None
            for label in fetched_mr['labels']:
                if not label.startswith('phase::'):
                    continue
                phase_label = label

            merge_requests.append((fetched_mr, phase_label))

            # Set phase::acceptance-testing label for MR
            if phase_label in ['phase::review', 'phase::lgtm', None]:
                self.logger.debug(f'set !{mr} to phase::acceptance-testing')
                self.set_mr_label(mr, 'phase::acceptance-testing')
                updated_merge_requests += 1
            elif phase_label != 'phase::finalized':
                self.logger.error(f'dunno what to do with !{mr}, "{phase_label}"')

            bar.update(i)
        bar.finish()\

        self.logger.info(f'updated labels for {updated_merge_requests} merge requests')

        # Makes no sense - fetched before the label is changed
        # for fetched, label in merge_requests:
        #     if label not in ['phase::acceptance-testing', 'phase::finalized']:
        #         self.logger.error(f'failed to handle !{fetched["iid"]}, label: {label}')

    def pipeline_status_for_tag(self, tag: str) -> CiStatus:
        self.logger.debug(f'looking for ci-job for "{tag}"')
        resp = self.http.get(f'/projects/{self.project_id}/pipelines?ref={tag}')

        if resp.status_code == 404:
            return None

        result = resp.json()

        if len(result) == 0:
            return None

        pipeline_id = result[0]['id']
        ci_status = result[0]['status']

        if ci_status == 'running':
            self.logger.debug(f'pipeline is running. Finding job information for pipeline {pipeline_id}')
            resp = self.http.get(f'/projects/{self.project_id}/pipelines/{pipeline_id}/jobs')
            result = resp.json()
            completed = [x['status'] for x in result]
            successful_jobs = 0
            pending_jobs = 0
            for job in completed:
                if job == 'success':
                    successful_jobs += 1
                if job == 'pending':
                    pending_jobs += 1

            return CiStatus(pipeline_id, ci_status, len(result), successful_jobs, pending_jobs)
        return CiStatus(pipeline_id, ci_status)

    def get_release(self, tag: str):
        self.logger.debug(f'looking for release with tag {tag}')
        resp = self.http.get(f'/projects/{self.project_id}/releases/{tag}')

        if resp.status_code == 404:
            self.logger.warning(f"couldn't find a release with tag {tag}")
            return None

        return resp.json()

    def post_release(self, tag: str, change_log: str):
        self.logger.debug(f'creating a release for {tag}')
        resp = self.http.post_json(f'/projects/{self.project_id}/releases', {
            'ref': tag,
            'description': change_log
        })

        if resp.status_code == 409:
            gitlab_link = f'https://gitlab.com/consensusaps/connect/-/releases/{tag}'
            import pyperclip
            pyperclip.copy(gitlab_link)
            self.logger.error(f"couldn't create a release with {tag} as it already exists: {gitlab_link} (in clipboard)")

class Tag:
    def __init__(self, name, message):
        self.name = name
        self.message = message

class CiStatus:
    def __init__(self, id, status: str, job_count = 0, completed_jobs = 0, pending_jobs = 0):
        self.id = id
        self.status = status
        self.job_count = job_count
        self.completed_jobs = completed_jobs
        self.pending_jobs = pending_jobs
