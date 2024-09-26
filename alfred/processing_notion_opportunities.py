import structlog
from django.db import transaction

from alfred.notion_handler import notion_handler
from data.models import Activity, BerlinLocation, Language, Opportunity, TargetGroup

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


def create_opportunity_from_notion(notion_record: dict):
    try:
        with transaction.atomic():
            properties = notion_record["properties"]
            vo_information = (
                properties["VO information"]["rich_text"][0]["text"]["content"]
                if properties["VO information"]["rich_text"]
                else None
            )
            volunteers_number = (
                int(properties["Number of volunteers needed"]["select"]["name"])
                if properties["Number of volunteers needed"]["select"]
                else 1
            )

            opportunity = Opportunity(
                title=properties["Name"]["title"][0]["text"]["content"],
                notion_id=notion_record["id"],
                last_edited_time_notion=notion_record["last_edited_time"],
                status=properties["Status"]["status"]["name"],
                volunteers_number=volunteers_number,
                vo_information=vo_information,
            )
            opportunity.save()

            target_groups = properties["Target group"]["multi_select"]
            for group in target_groups:
                target_group, _ = TargetGroup.objects.get_or_create(title=group["name"])
                opportunity.target_groups.add(target_group)

            schedules = properties["Schedule"]["multi_select"]
            schedule_str = ""
            for schedule in schedules:
                schedule_str += f" {schedule['name']}"
            opportunity.schedule_str = schedule_str

            languages = properties["Languages needed"]["multi_select"]
            for lang in languages:
                match lang["name"]:
                    case "Farsi":
                        lang["name"] = "Persian"
                    case "Romanes" | "Any" | "no specific language needed":
                        continue

                language = Language.objects.filter(title=lang["name"]).first()
                opportunity.languages.add(language)

            districts = properties["District"]["multi_select"]
            for district in districts:
                location, _ = BerlinLocation.objects.get_or_create(
                    name=district["name"]
                )
                opportunity.berlin_locations.add(location)

            skills = properties["Type"]["multi_select"]
            for skill in skills:
                skill, _ = Activity.objects.get_or_create(title=skill["name"])
                opportunity.activities.add(skill)

            opportunity.save()

    except Exception as e:
        logger.error(
            f"Error processing opportunity: {str(e)} url {notion_record['url']}"
        )


def remove_deleted_records(notion_results: list[dict]) -> None:
    if not notion_results or len(notion_results) == 0:
        logger.info("Notion table is empty")
        return

    for_deletion = Opportunity.objects.none()
    for record in notion_results:
        try:
            notion_id = record["id"]
            for_deletion |= Opportunity.objects.filter(notion_id=notion_id)
        except (KeyError, TypeError) as e:
            logger.error(f"Error {str(e)} in Notion record {record=}")
            return

    try:
        count = for_deletion.delete()
        logger.info(f"Deleted {count} of opportunities")
    except Exception as e:
        logger.error(
            f"An exception {e} occured while trying to delete Notion table deleted records"
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
                logger.debug("Last edited time changed")
                delete_opportunity(notion_id=notion_id)
                create_opportunity_from_notion(notion_record=record)

    except Exception as e:
        logger.error(f"Error processing opportunity: {str(e)}")
        raise
