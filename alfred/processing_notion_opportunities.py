import structlog
from django.db import transaction

from alfred.notion_handler import notion_handler
from data.models import (
    Activity,
    BerlinLocation,
    Language,
    Opportunity,
    OpportunityLanguageM2M,
    OpportunityType,
)

logger = structlog.get_logger(__name__)


def opportunity_not_exists(notion_id: str) -> bool | None:
    try:
        opportunities = Opportunity.objects.filter(notion_id=notion_id)
        count = opportunities.count()
        if count == 0:
            return True
        elif count == 1:
            return False
        else:
            logger.error(f"Multiple opportunities found with {notion_id=}")

    except Exception as e:
        logger.error(f"Error checking opportunity: {str(e)}")


def delete_opportunity(notion_id: str) -> None:
    logger.debug(f"Should delete the opportunity with {notion_id=}")
    opportunity = Opportunity.objects.get(notion_id=notion_id)
    opportunity.delete()


def opportunity_last_edited_time_changed(
    notion_id: str, last_edited_time
) -> bool | None:
    try:
        opportunities = Opportunity.objects.filter(
            notion_id=notion_id, last_edited_time_notion=last_edited_time
        )
        count = opportunities.count()
        if count == 0:
            return True
        elif count == 1:
            return False

    except Exception as e:
        logger.error(f"Error checking opportunity: {str(e)} {notion_id=}")


def should_be_processed(notion_record: dict) -> bool | None:
    notion_id = notion_record["id"]
    return opportunity_not_exists(notion_id=notion_id)


def add_languages_to_opportunity(languages, opportunity_obj):
    for language in languages:
        match language["name"]:
            case "Farsi":
                language["name"] = "Persian"
            case "Romanes" | "Any" | "no specific language needed":
                continue

        language_obj = Language.objects.filter(title=language["name"]).first()
        if language_obj:
            OpportunityLanguageM2M.objects.create(
                language=language_obj, opportunity=opportunity_obj
            )


def create_opportunity_from_notion(notion_record: dict):
    try:
        with transaction.atomic():
            properties = notion_record["properties"]

            vo_information = (
                properties["VO information"]["rich_text"][0]["text"]["content"]
                if properties["VO information"]["rich_text"]
                else None
            )
            datetime_str = (
                properties["Date, time"]["date"]["start"]
                if properties["Date, time"]["date"]
                else None
            )
            volunteers_number = (
                int(properties["Number of volunteers needed"]["select"]["name"])
                if properties["Number of volunteers needed"]["select"]
                else 1
            )

            opportunity_type = (
                properties.get("Opp Type", {})
                .get("select", {})
                .get("name", OpportunityType.GENERAL)
            )

            opportunity = Opportunity(
                title=properties["Name"]["title"][0]["text"]["content"],
                notion_id=notion_record["id"],
                last_edited_time_notion=notion_record["last_edited_time"],
                opportunity_type=opportunity_type,
                status=properties["Status"]["status"]["name"],
                datetime_str=datetime_str,
                volunteers_number=volunteers_number,
                vo_information=vo_information,
            )
            opportunity.save()

            schedules = properties["VO Schedule"]["multi_select"]
            schedule_str = ""
            for schedule in schedules:
                schedule_str += f" {schedule['name']}"
            opportunity.schedule_str = schedule_str

            add_languages_to_opportunity(
                languages=properties["Refugee Languages"]["multi_select"],
                opportunity_obj=opportunity,
            )

            add_languages_to_opportunity(
                languages=properties["Translation Languages"]["multi_select"],
                opportunity_obj=opportunity,
            )

            districts = properties["District VO"]["multi_select"]
            for district in districts:
                location, _ = BerlinLocation.objects.get_or_create(
                    name=district["name"]
                )
                opportunity.berlin_locations.add(location)

            activities = properties["Type"]["multi_select"]
            for activity in activities:
                activity, _ = Activity.objects.get_or_create(title=activity["name"])
                opportunity.activities.add(activity)

            opportunity.save()

    except Exception as e:
        logger.error(
            f"Notion record number {notion_record["properties"]["ID"]["unique_id"]["number"]} || Error processing opportunity: at {str(e)} url {notion_record['url']}"
        )


def remove_deleted_records(notion_results: list[dict]) -> None:
    if not notion_results:
        logger.info("Notion table is empty")
        return

    opportunity_notion_ids = [
        str(opportunity.notion_id) for opportunity in Opportunity.objects.all()
    ]

    notion_results_ids = [record["id"] for record in notion_results]

    notion_ids_for_deletion = list(
        set(opportunity_notion_ids) - set(notion_results_ids)
    )

    if not notion_ids_for_deletion:
        logger.info("No records to delete")
        return
    logger.debug(f"{notion_ids_for_deletion=}")

    try:
        deleted_objects = Opportunity.objects.filter(
            notion_id__in=notion_ids_for_deletion
        ).delete()
        logger.info(f"Deleted {deleted_objects} from Opportunities")
    except Exception as e:
        logger.error(
            f"An exception {e} occurred while trying to delete objects that have been removed from Notion table"
        )


def execute_opportunities_pipeline():
    notion_data = notion_handler.get_database_data()
    notion_results = notion_data["results"]  # type: ignore
    logger.info(f"Got {len(notion_results)} results")

    remove_deleted_records(notion_results)

    try:
        for record in notion_results:
            notion_id = record["id"]
            last_edited_time_notion = record["last_edited_time"]

            if opportunity_not_exists(notion_id=notion_id):
                if not record["properties"]["Name"]["title"]:
                    logger.error(f"Empty opportunity; url {record['url']}")
                    continue
                logger.debug(f"Start creating notion record {notion_id=}")
                create_opportunity_from_notion(notion_record=record)

            elif opportunity_last_edited_time_changed(
                notion_id=notion_id, last_edited_time=last_edited_time_notion
            ):
                logger.debug(
                    f"Opportunity {notion_id=}; last edited time has been changed"
                )
                delete_opportunity(notion_id=notion_id)
                create_opportunity_from_notion(notion_record=record)

    except Exception as e:
        logger.error(f"Error processing opportunity: {str(e)}")
        raise
