import structlog
from celery import shared_task

from alfred.processing_notion_opportunities import execute_opportunities_pipeline
from alfred.utils import read_env_var

logger = structlog.get_logger(__name__)


@shared_task
def process_opportunities():
    env = read_env_var("ENVIRONMENT")
    if env == "PRODUCTION":
        try:
            logger.info("Attempting to pull opportunities")
            execute_opportunities_pipeline()
        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)
    else:
        logger.info("Celery detected not production env, skipping the task")
