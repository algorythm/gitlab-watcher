from src.common.logging_helper import get_logger
from src.common.http_helper import Http

# https://api.slack.com/messaging/webhooks
class SlackPoster:
    def __init__(self, post_hook: str):
        self.logger = get_logger(__name__)
        self.http = Http(post_hook)
        pass

    def post_message(self, message: str):
        pass

    def test(self):
        # body = {
        #     "text": "Hello, World! This is a test",
        #     "blocks": [
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": "# This is a heading\nHello, World!"
        #             },
        #         },
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": "- bullet points\n- bullet two\n- bullet three"
        #             },
        #         },
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": "[my awesome link](https://www.google.com)"
        #             },
        #             "accessory": "image",
        #             "image_url": "http://www.consensus.dk/boost/wp-content/uploads/2018/01/CO_Logo_RGB.png",
        #             "alt_text": "my awesome image"
        #         }
        #     ]
        # }
        # resp = self.http.post_json('', body)
        resp = self.http.post_json('', {'text': 'Hello, World!'})
