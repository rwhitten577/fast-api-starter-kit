import logging
from distutils.util import strtobool
from typing import Dict, Any, List

from src.core.settings import Settings
from slack import WebClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackConnector:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.environment = settings.ENVIRONMENT
        self.client = WebClient(token=self.settings.SLACK_API_TOKEN)

    def send_slack_alert(self, message: str, app_name: str = None, job_owner_id: str = None):
        if not bool(strtobool(self.settings.SLACK_ENABLED)):
            logger.info("Trying to send message to Slack but it is not enabled.")
            return

        app_name = app_name or self.settings.PROJECT_NAME

        attachment = {
            "pretext": f"*Alert from `{self.environment.upper()}` `{app_name}`*",
            "mrkdwn_in": ["text", "pretext"],
            "color": "danger",
            "text": message
        }

        # Send to default channel
        channel = self.settings.SLACK_CHANNEL_ID
        self._slack_post_message(channel, [attachment])

    def _slack_post_message(self, channel: str, attachments: List[Dict[str, Any]],
                            retry_count: int = 3):
        retries = retry_count

        while retries > 0:
            try:
                self.client.chat_postMessage(channel=channel, attachments=attachments)
                break
            except SlackApiError as e:
                retries -= 1
                logger.exception("Error sending slack alert.")

                if retries == 0:
                    raise e
