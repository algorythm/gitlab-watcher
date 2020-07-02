from __future__ import annotations
from typing import List
from src.config import ConfigReader, WatcherConfig
from src.gitlab import GitLab

from src.common.logging_helper import get_logger
from src.watcher_job import GitLabWatcher
from src.common.change_log import Change
from datetime import datetime

from src.common.file_editor import write_temp_file
from src.slack_poster import SlackPoster
import argparse, traceback, re

# Changelog format: https://keepachangelog.com/en/1.0.0/
def main(config: WatcherConfig, tag: str = None):
    logger = get_logger(__name__)
    gl = GitLab(config.gitlab_config.project_id, config.gitlab_config.token)
    sp = SlackPoster(config.slack_config)

    if tag == None:
        tag = gl.latest_tag()
    else:
        tag = gl.get_tag(tag)

    changes = list_mr_ids(tag.message)

    change_log, markdown = format_changelog(tag.name, changes)
    markdown = write_temp_file('md', markdown, 'nvim')

    mrs_to_change = [c.mr for c in changes]
    logger.info(f'check labels for labels {mrs_to_change}')
    gl.change_mr_labels(mrs_to_change)

    gl.post_release(tag.name, markdown)
    if sp.config.configured:
        sp.post_change_log(tag.name, change_log)

def list_latest_releases(config: WatcherConfig, tag: str = None):
    """
    Displays the latest 10 releases on GitLab
    """

    gl = GitLab(config.gitlab_config.project_id, config.gitlab_config.token)
    latest_tag = gl.latest_tag()
    # releases = gl.get_release()

    if tag == None:
        latest_tags = gl.get_tag()
    else:
        latest_tags = [gl.get_tag(tag)]
    tags_formatted = []

    for tag in latest_tags:
        release_exists = False

        release = gl.get_release(tag.name)

        if release != None:
            release_exists = True

        tags_formatted.append((tag.name, release_exists))

    print(f'Latest Tag: {latest_tag.name}\n')

    for name, release_exists in tags_formatted:
        exists = '?'
        if release_exists:
            exists = '+'
        else:
            exists = '-'

        print(f'- {name} [{exists}]')

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
    scope = ''
    if change.scope != '' or change.scope != None:
        scope = f'**{change.scope.strip()}**: '

    return f'- **{scope}**: {change.message.strip()} [[!{change.mr}](https://gitlab.com/consensusaps/connect/-/merge_requests/{change.mr})]\n'

def list_mr_ids(message: str) -> List[Change]:
    changes = []
    for line in message.splitlines()[2::]:
        changes.append(Change(line))
    return changes

if __name__ == '__main__':
    config = ConfigReader().read_config()

    parser = argparse.ArgumentParser(description='Automate changelogs and releases on GitLab')
    parser.add_argument('tag', type=str, nargs='?', help='specify a specific tag to apply for', default=None)
    parser.add_argument('--display', '-d', action='store_true', help='shows 10 latest tags and release on GitLab')
    args = parser.parse_args()

    try:
        if args.display:
            list_latest_releases(config, args.tag)
        elif args.tag != None:
            # print(f'using tag {args.tag}')
            main(config, args.tag)
        else:
            main(config)
    except Exception as e:
        print(e)
        print()
        track = traceback.format_exc()
        # print('---')
        # print(track)
        # print('---')

        changes = re.findall(r'File "((\w|\.|-|\_|\/|\\|\d+)+)", line (\d+)', track)
        for change in changes:
            if len(change) < 3:
                continue
            file = change[0]
            line = change[2]
            print(f'{file}, line {line}')
