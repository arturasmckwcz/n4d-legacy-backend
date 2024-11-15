import structlog
from celery import shared_task

from alfred.processing_notion_opportunities import execute_opportunities_pipeline
from alfred.processing_notion_volunteerform import (
    execute_volunteerform_pipeline,
    execute_volunteerform_seed_pipeline,
)
from alfred.settings import FF_VOLUNTEER_CONNECTOR
from alfred.utils import read_env_var

logger = structlog.get_logger(__name__)

is_debugging = read_env_var("DEBUG")
is_production = read_env_var("ENVIRONMENT") == "PRODUCTION"


@shared_task
def process_opportunities():
    if is_production or is_debugging:
        try:
            logger.info("Attempting to pull opportunities")
            execute_opportunities_pipeline()
        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)
    else:
        logger.info("Celery detected wrong environment, skipping the task")


@shared_task
def process_volunteerform():
    if FF_VOLUNTEER_CONNECTOR:
        if is_production or is_debugging:
            try:
                logger.info("Attempting to pull volunteerform")
                execute_volunteerform_pipeline()
            except Exception as e:
                logger.error(f"Error occurred: {e}", exc_info=True)
        else:
            logger.info("Celery detected wrong environment, skipping the task")
    else:
        logger.info(
            "Celery detected VOLUNTEER_CONNECTOR is negative, skipping the task"
        )


@shared_task
def process_seed_volunteerform():
    if FF_VOLUNTEER_CONNECTOR:
        if is_production or is_debugging:
            try:
                logger.info("Attempting to seed volunteerform")
                execute_volunteerform_seed_pipeline()
            except Exception as e:
                logger.error(f"Error occurred: {e}", exc_info=True)
        else:
            logger.info("Celery detected wrong environment, skipping the task")
    else:
        logger.info(
            "Celery detected VOLUNTEER_CONNECTOR is negative, skipping the task"
        )
