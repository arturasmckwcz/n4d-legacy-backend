from typing import Callable

import structlog
from celery import shared_task

from alfred.processing_notion_opportunities import (
    execute_opportunities_seed_pipeline,
    execute_opportunities_sync_pipeline,
)
from alfred.processing_notion_volunteerform import (
    execute_volunteerform_pipeline,
    execute_volunteerform_seed_pipeline,
)
from alfred.settings import ENV
from alfred.utils import read_env_var
from data.enums import Environment

logger = structlog.get_logger(__name__)

is_debugging = read_env_var("DEBUG")
is_production = ENV == Environment.PRODUCTION


def exec_pipeline(fn: Callable, info_msg: str):
    if is_production or is_debugging:
        try:
            logger.info(info_msg)
            fn()
        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)
    else:
        logger.info("Celery detected wrong environment, skipping the task")


@shared_task
def process_sync_opportunities():
    exec_pipeline(
        fn=execute_opportunities_sync_pipeline,
        info_msg="Attempting to sync opportunities",
    )


@shared_task
def process_pull_opportunities():
    exec_pipeline(
        fn=execute_opportunities_seed_pipeline,
        info_msg="Attempting to pull opportunities",
    )


@shared_task
def process_sync_volunteerform():
    exec_pipeline(
        fn=execute_volunteerform_pipeline, info_msg="Attempting to sync volunteerform"
    )


@shared_task
def process_pull_volunteerform():
    exec_pipeline(
        fn=execute_volunteerform_seed_pipeline,
        info_msg="Attempting to pull volunteerform",
    )
