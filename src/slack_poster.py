from __future__ import annotations
from src.common.logging_helper import get_logger
from src.common.http_helper import Http
from src.config import SlackConfig
from src.common.change_log import Change

# https://api.slack.com/messaging/webhooks
class SlackPoster:
    def __init__(self, config: SlackConfig):
        self.config = config
        if not self.config.configured:
            return
        self.logger = get_logger(__name__)

        self.http = Http('https://slack.com/api')
        self.http.add_header('Authorization', f'Bearer {self.config.token}')

    def post_change_log(self, version, change_log):
        blocks = []
        gitlab_release = f'https://gitlab.com/consensusaps/connect/-/releases/{version}'

        blocks.append(MessageBuilder().create_block(f'Deployed version *<{gitlab_release}|{version}>*. These changes are best viewed on GitLab, as they are more up to date there, but for a summary is included here for a quick overview.'))
        blocks.append(MessageBuilder().create_divider())

        for key in change_log:
            if len(change_log[key]) == 0:
                continue

            fields = ''
            for change in change_log[key]:
                fields += f'• {change.message} [<https://gitlab.com/consensusaps/connect/-/merge_requests/{change.mr}|!{change.mr}>]\n'
            blocks.append(MessageBuilder().create_block(f'*{key}*\n{fields}'))

        blocks.append(MessageBuilder().create_context(f'*Version*: {version}'))
        blocks.append(MessageBuilder().create_link_button('View on GitLab', gitlab_release))

        body = {
            'channel': self.config.changelog_channel,
            'blocks': blocks
        }

        self.logger.debug(f'posting changelog for {version} to #{body["channel"]}')
        resp = self.http.post_json('/chat.postMessage', body)

        error = self.parse_error(resp)
        if error != None:
            self.logger.error(f'failed to post on Slack: {error}')

    def parse_error(self, response) -> str:
        json = response.json()

        if json['ok'] == False:
            return json['error']
        return None

class MessageBuilder:
    def __init__(self):
        pass

    def create_block(self, text):
        return {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': text
            }
        }

    def create_divider(self):
        return {
            'type': 'divider'
        }

    def create_field(self, *lines):
        field = { 'type': 'section', 'fields': []}
        for line in lines:
            field['fields'].append({
                'type': 'plain_text',
                'text': line,
                'emoji': True
            })
        return field

    def create_link_button(self, text, url):
        return {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': ' '
            },
            'accessory': {
                'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'text': text
                },
                'style': 'primary',
                'url': url
            }
        }

    def create_context(self, *elements):
        elms = []

        for element in elements:
            elms.append({ 'type': 'mrkdwn', 'text': element })

        return {
            'type': 'context',
            'elements': elms
        }
