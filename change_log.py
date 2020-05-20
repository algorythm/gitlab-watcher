from __future__ import annotations
from typing import List
# from src.config import get_env
from src.config import ConfigReader, WatcherConfig
from src.gitlab import GitLab

from src.common.logging_helper import get_logger
from src.watcher_job import GitLabWatcher
# import re
from src.common.change_log import Change
from datetime import datetime

from src.common.file_editor import write_temp_file
from src.slack_poster import SlackPoster
import sys

# Changelog format: https://keepachangelog.com/en/1.0.0/
def main(config: WatcherConfig, tag: str = None):
    gl = GitLab(config.gitlab_config.project_id, config.gitlab_config.token)
    sp = SlackPoster(config.slack_config)

    if tag == None:
        tag = gl.latest_tag()
    else:
        tag = gl.get_tag('v2.0.53')

    changes = list_mr_ids(tag.message)

    change_log, markdown = format_changelog(tag.name, changes)
    markdown = write_temp_file('md', markdown, 'nvim')

    gl.post_release(tag.name, markdown)
    sp.post_change_log(tag.name, change_log)

def format_changelog(version_number: str, changes: List[Change]):
    breaking = []
    additions = []
    removed = []
    changed = []
    fixes = []
    other = []

    for change in changes:
        if change.is_breaking == True:
            breaking.append(change)
            continue
        if change.change_type == 'feat':
            additions.append(change)
            continue
        if change.change_type == 'refactor':
            changed.append(change)
            continue
        if change.change_type == 'revert':
            removed.append(change)
            continue
        if change.change_type == 'fix':
            fixes.append(change)
            continue
        else:
            other.append(change)
            continue
    base = f'## [{version_number}](https://gitlab.com/consensusaps/connect/-/tags/{version_number}) - {datetime.now().strftime("%Y-%m-%d")}\n'

    change_log = {
        'Breaking Changes': breaking,
        'Added': additions,
        'Changed': changed,
        'Deprecated': [],
        'Removed': removed,
        'Fixed': fixes,
        'Security': [],
        'Other': other,
    }

    for key in change_log:
        base += f'### {key}\n'
        if len(change_log[key]) == 0:
            base += '\n'
            continue

        for change in change_log[key]:
            base += format_row(change)
        base += '\n'

    return change_log, base

def format_row(change: Change) -> str:
    return f'- {change.message.strip()} [!{change.mr}](https://gitlab.com/consensusaps/connect/-/merge_requests/{change.mr})\n'

def list_mr_ids(message: str) -> List[Change]:
    changes = []
    for line in message.splitlines()[2::]:
        changes.append(Change(line))
    return changes

if __name__ == '__main__':
    config = ConfigReader().read_config()
    if len(sys.argv) == 2:
        main(config, tag = sys.argv[1])
    else:
        main(config)
