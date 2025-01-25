import ssl

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from alfred.utils import read_env_var

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_token = str(read_env_var("SLACK_BOT_TOKEN"))

client = WebClient(token=slack_token, ssl=ssl_context)

logger = structlog.get_logger(__name__)


def slack_post_message(message: str, dry_run=False) -> None:
    if dry_run or slack_token == "test":
        logger.debug(f"Slack would send {message}")
    else:
        try:
            client.chat_postMessage(channel="C07ANBJ9SSU", text=message)
        except SlackApiError as e:
            logger.error(f"SlackAPI error: {e}")
