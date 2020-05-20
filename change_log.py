from __future__ import annotations
from typing import List
from src.config import get_env
from src.gitlab import GitLab

from src.common.logging_helper import get_logger
from src.watcher_job import GitLabWatcher
import re
from datetime import datetime

from src.common.file_editor import write_temp_file
from src.slack_poster import SlackPoster

# Changelog format: https://keepachangelog.com/en/1.0.0/
def main(config_path: str):
    config = get_env(config_path)
    gl = GitLab(17170378, config['gitlab']['token'])
    tag = gl.latest_tag()

    changes = list_mr_ids(tag.message)

    change_log = write_temp_file('md', format_changelog(tag.name, changes), 'nvim')
    gl.post_release(tag.name, change_log)

def format_changelog(version_number: str, changes: List[Change]) -> str:
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

    base += '### Breaking Changes\n'
    for change in breaking:
        base += format_row(change)

    base += '\n'
    base += '### Added\n'
    for change in additions:
        base += format_row(change)

    base += '\n'
    base += '### Changed\n'
    for change in changes:
        base += format_row(change)

    base += '\n'
    base += '### Deprecated\n'

    base += '\n'
    base += '### Removed\n'

    base += '\n'
    base += '### Fixed\n'
    for change in fixes:
        base += format_row(change)

    base += '\n'
    base += '### Security\n'

    base += '\n'
    base += '### Other\n'
    for change in fixes:
        base += format_row(change)

    base += '\n'

    return base

def format_row(change: Change) -> str:
    return f'- {change.message.strip()} [!{change.mr}](https://gitlab.com/consensusaps/connect/-/merge_requests/{change.mr})\n'

def list_mr_ids(message: str) -> List[Change]:
    changes = []
    for line in message.splitlines()[2::]:
        changes.append(Change(line))
    return changes

class Change:
    def __init__(self, message):
        change_type, scope, message, mr = self.split(message)
        self.change_type = change_type
        self.scope = scope
        self.message = message
        self.mr = mr
        self.is_breaking = False

    def split(self, line):
        return re.findall(r'(\w+)(?:\(([^\)]+)\))?:\s?([^\[]+)?\s?\[!(\d+)\]', line)[0]

if __name__ == '__main__':
    main('env.yml')
    # config = get_env('env.yml')
    # sp = SlackPoster(config['slack']['post_changelog_hook'])
    # sp.test()
