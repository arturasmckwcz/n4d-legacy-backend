import ssl

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from alfred.utils import read_env_var

logger = structlog.get_logger(__name__)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

token = str(read_env_var("SLACK_BOT_TOKEN"))
channel = str(read_env_var("SLACK_CHANNEL_NEW_ARRIVALS"))

try:
    client = WebClient(token=token, ssl=ssl_context)
except SlackApiError as e:
    logger.error(f"Error creating Slack client: {e.response['error']}")
    client = None


def slack_post_message(message: str, dry_run=False) -> None:
    if dry_run or token == "test":
        logger.debug(f"Slack would send {message}")
    else:
        try:
            if client is None:
                logger.error("Slack client is not initialized.")
                return

            client.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            logger.error(f"SlackAPI error: {e}")
