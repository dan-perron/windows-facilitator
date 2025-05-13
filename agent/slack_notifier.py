import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agent.config import SLACK_BOT_TOKEN, SLACK_CHANNEL

class SlackNotifier:
    def __init__(self, slack_token=None, slack_channel=None):
        self.logger = logging.getLogger(__name__)
        self.slack_token = slack_token or SLACK_BOT_TOKEN
        self.slack_channel = slack_channel or SLACK_CHANNEL
        self.client = None
        if self.slack_token:
            self.client = WebClient(token=self.slack_token)

    def send_message(self, text, channel=None):
        if not self.client or not (channel or self.slack_channel):
            self.logger.warning("Slack client or channel not configured.")
            return
        try:
            self.client.chat_postMessage(
                channel=channel or self.slack_channel,
                text=text
            )
            self.logger.info(f"Sent Slack message: {text}")
        except SlackApiError as e:
            self.logger.error(f"Failed to send Slack message: {e.response['error']}")

    def send_file(self, file_path, message=None, channel=None):
        if not self.client or not (channel or self.slack_channel):
            self.logger.warning("Slack client or channel not configured.")
            return
        try:
            self.client.files_upload_v2(
                channel=channel or self.slack_channel,
                file=file_path,
                initial_comment=message or ""
            )
            self.logger.info(f"Sent file to Slack: {file_path}")
        except SlackApiError as e:
            self.logger.error(f"Failed to send file to Slack: {e.response['error']}") 