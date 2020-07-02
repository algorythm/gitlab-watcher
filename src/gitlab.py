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

    def get_tag(self, tag: str = None) -> Tag:
        self.logger.debug(f'fetching tag {tag} from GitLab')

        if tag != None:
            resp = self.http.get(f'/projects/{self.project_id}/repository/tags/{tag}')
        else:
            resp = self.http.get(f'/projects/{self.project_id}/repository/tags')

        if resp.status_code == 404:
            self.logger.warning(f"couldn't find tag {tag}")
            return None

        result = resp.json()

        if tag != None:
            return Tag(result['name'], result['message'])
        else:
            tags = []
            for x in result:
                tags.append(Tag(x['name'], x['message']))
            return tags

    def get_release(self, tag: str = None):
        self.logger.debug(f'looking for release with tag {tag}')
        self.logger.debug(self.project_id)
        if tag != None:
            try:
                resp = self.http.get(f'/projects/{self.project_id}/releases/{tag}')
            except:
                return None
        else:
            resp = self.http.get(f'/projects/{self.project_id}/releases')

        if resp.status_code == 404:
            self.logger.warning(f"couldn't find a release with tag {tag}")
            return None

        return resp.json()

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
            dev_only = False
            fetched_mr = self.get_merge_request(mr, True)

            # Get phase status for MR
            phase_label = None
            for label in fetched_mr['labels']:
                if not label.startswith('phase::'):
                    continue
                phase_label = label
                if label == 'impact::dev_only':
                    dev_only = True

            merge_requests.append((fetched_mr, phase_label))

            # Set phase::acceptance-testing label for MR
            if phase_label == 'phase::review' and not dev_only:
                self.logger.debug(f'set !{mr} to phase::acceptance-testing')
                self.set_mr_label(mr, 'phase::acceptance-testing')
                updated_merge_requests += 1
            elif phase_label == 'phase::review' and dev_only:
                self.logger.debug(f'set !{mr} to phase::finalized')
                self.set_mr_label(mr, 'phase::finalized')
                updated_merge_requests += 1
            elif phase_label != 'phase::finalized' and phase_label != 'phase::acceptance-testing':
                self.logger.error(f'dunno what to do with !{mr}, "{phase_label}"')

            bar.update(i)
        bar.finish()

        self.logger.info(f'updated labels for {updated_merge_requests} merge requests')

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

    def post_release(self, tag: str, change_log: str):
        self.logger.debug(f'creating a release for {tag}')
        resp = self.http.post_json(f'/projects/{self.project_id}/releases', {
            'ref': tag,
            'tag_name': tag,
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
