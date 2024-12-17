from datetime import datetime

import structlog
from django.db import transaction

from alfred.config.globals import comments_delimiter, comments_none
from alfred.notion_handler import NotionHandler
from alfred.utils import (
    get_clean_select_for_notion,
    get_database_object,
    get_key_value,
    get_list,
    get_schedule_list,
    get_the_first,
    is_later_than,
    read_env_var,
)
from data.models import (
    Activity,
    BerlinLocation,
    Language,
    Opportunity,
    OpportunityLanguageM2M,
    OpportunityType,
)

logger = structlog.get_logger(__name__)

notion_database_id = read_env_var("NOTION_OPPORTUNITIES_ID")
notion_handler = NotionHandler(notion_database_id)


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


def create_or_update_opportunity_from_notion(
    notion_record: dict, update_object: Opportunity | None = None
):
    try:
        with transaction.atomic():
            if update_object:
                success, deleted_dict = update_object.delete()

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
            ).lower()
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
                languages=properties["Translation"]["multi_select"],
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
    notion_results = notion_handler.get_database_data()
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
                create_or_update_opportunity_from_notion(notion_record=record)

            elif opportunity_last_edited_time_changed(
                notion_id=notion_id, last_edited_time=last_edited_time_notion
            ):
                logger.debug(
                    f"Opportunity {notion_id=}; last edited time has been changed"
                )
                opportunity_object = Opportunity.objects.get(notion_id=notion_id)
                create_or_update_opportunity_from_notion(
                    notion_record=record, update_object=opportunity_object
                )

    except Exception as e:
        logger.error(f"Error processing opportunity: {str(e)}")
        raise


def prepare_opportunity_data_for_db(opportunity_page: dict) -> tuple | None:
    opportunity_data = {}
    try:
        opportunity_data["notion_id"] = opportunity_page["id"]

        title = get_the_first(
            opportunity_page["properties"]["Name"]["title"], should_raise=True
        )
        opportunity_data["title"] = get_key_value(
            title, ["text", "content"], should_raise=True
        )

        address = get_the_first(opportunity_page["properties"]["Address"]["rich_text"])
        opportunity_data["accomp_address"] = get_key_value(address, ["plain_text"])

        aaDate = get_key_value(
            opportunity_page, ["properties", "Date, time", "date", "start"]
        )
        opportunity_data["accomp_datetime"] = (
            datetime.fromisoformat(aaDate) if aaDate else None
        )

        aaInfo = get_the_first(
            opportunity_page["properties"]["AA Information"]["rich_text"]
        )
        opportunity_data["accomp_information"] = get_key_value(aaInfo, ["plain_text"])

        aaName = get_the_first(
            opportunity_page["properties"]["Refugee Name"]["rich_text"]
        )
        opportunity_data["accomp_name"] = get_key_value(aaName, ["plain_text"])

        aaPhone = get_the_first(
            opportunity_page["properties"]["Refugee Phone"]["rich_text"]
        )
        opportunity_data["accomp_phone"] = get_key_value(aaPhone, ["plain_text"])

        aaPLZ = get_the_first(opportunity_page["properties"]["Postcode"]["rich_text"])
        opportunity_data["accomp_postcode"] = get_key_value(aaPLZ, ["plain_text"])

        aaTranslate = get_the_first(
            opportunity_page["properties"]["Translation"]["multi_select"]
        )
        opportunity_data["accomp_translation"] = get_key_value(aaTranslate, ["name"])

        opportunity_data["opportunity_type"] = get_key_value(
            opportunity_page, ["properties", "Opp Type", "select", "name"]
        )

        opportunity_data["status"] = get_key_value(
            opportunity_page, ["properties", "Status", "status", "name"]
        )

        volunteers_number = get_key_value(
            opportunity_page,
            ["properties", "Number of volunteers needed", "select", "name"],
        )
        opportunity_data["volunteers_number"] = int(volunteers_number) or 1

        voInfo = get_the_first(
            opportunity_page["properties"]["VO information"]["rich_text"]
        )
        opportunity_data["vo_information"] = get_key_value(voInfo, ["plain_text"])

        racInfo = get_the_first(
            opportunity_page["properties"]["RAC Contact"]["rich_text"]
        )
        racInfo = get_key_value(racInfo, ["plain_text"])
        racInfo = racInfo.split(comments_delimiter)
        if len(racInfo) == 5:
            rac_full_name, rac_email, rac_phone, rac_address, rac_plz = racInfo
            opportunity_data["rac_full_name"] = rac_full_name
            opportunity_data["rac_email"] = rac_email
            opportunity_data["rac_phone"] = rac_phone
            opportunity_data["rac_address"] = rac_address
            opportunity_data["rac_plz"] = rac_plz

    except Exception as e:
        logger.error(
            f"Error {repr(e)} occurred while processing Notion page id={opportunity_page['id']} structure. Skipping."
        )
        return None
    return (opportunity_data, {})  # returning m2m for consistency purposes


def write_or_update_opportunity_to_db(
    opportunity_page: dict, update_object: Opportunity | None = None
):
    data = prepare_opportunity_data_for_db(opportunity_page)

    if not data:
        return

    opportunity_data, m2m_data = data

    try:
        with transaction.atomic():
            if update_object:
                success, deleted_dict = update_object.delete()

            opportunity_object = Opportunity(**opportunity_data)
            opportunity_object.save()
    except Exception as e:
        logger.error(
            f"Error {repr(e)} occurred while writing Notion page id={opportunity_page['id']} to database. Skipping."
        )


def execute_opportunities_seed_pipeline():
    # 1. fetch opportunities from Notion
    opportunities_from_notion = notion_handler.get_database_data()

    logger.info(
        f"Found {len(opportunities_from_notion)} rows in Opportunities from Notion"
    )

    # 2. write Notion pages to the database
    for opportunity_page in opportunities_from_notion:
        write_or_update_opportunity_to_db(opportunity_page=opportunity_page)


def execute_opportunities_sync_pipeline():
    notion_database_id = read_env_var("NOTION_OPPORTUNITIES_ID")
    notion_handler = NotionHandler(notion_database_id)
    opportunities_from_notion = notion_handler.get_database_data()
    logger.info(f"Found {len(opportunities_from_notion)} rows in Opportunities")
    # 1. select updated in the Notion table and update db
    count = 0
    for opportunity_page in opportunities_from_notion:
        opportunity_object = get_database_object(opportunity_page, Opportunity)
        if opportunity_object and is_later_than(
            datetime.fromisoformat(opportunity_page["last_edited_time"]),
            opportunity_object.updated_at,
        ):
            count += 1
            write_or_update_opportunity_to_db(
                update_object=opportunity_object, opportunity_page=opportunity_page
            )
    logger.info(f"Updated {count} Opportunity objects")

    # 2. notion pages to be deleted from db
    notion_ids = [
        opportunity_page["id"] for opportunity_page in opportunities_from_notion
    ]
    opportunity_objects = (
        Opportunity.objects.filter()
        .exclude(notion_id__in=notion_ids)
        .exclude(notion_id=None)
    )
    logger.info(f"Attempting to remove {len(opportunity_objects)} Opportunity objects")
    opportunity_objects.all().delete()

    # 3. select new records in the DB and create new rows in the Notion table
    new_opportunity_objects = Opportunity.objects.filter(notion_id=None).all()
    logger.info(f"Found {len(new_opportunity_objects)} new Opportunity objects.")
    for new_opportunity in new_opportunity_objects:
        write_opportunity_to_notion(new_opportunity)


def write_opportunity_to_notion(opportunity: Opportunity):
    properties = {}
    properties["Name"] = {
        "title": [{"text": {"content": opportunity.title, "link": None}}]
    }
    if opportunity.accomp_address is not None:
        properties["Address"] = {
            "rich_text": [{"text": {"content": opportunity.accomp_address}}]
        }
    if opportunity.accomp_information is not None:
        properties["AA Information"] = {
            "rich_text": [{"text": {"content": opportunity.accomp_information}}]
        }
    if opportunity.accomp_name is not None:
        properties["Refugee Name"] = {
            "rich_text": [{"text": {"content": opportunity.accomp_name}}]
        }
    if opportunity.accomp_phone is not None:
        properties["Refugee Phone"] = {
            "rich_text": [{"text": {"content": opportunity.accomp_phone}}]
        }
    if opportunity.accomp_postcode is not None and isinstance(
        opportunity.accomp_postcode, int
    ):
        properties["Postcode"] = {
            "rich_text": [{"text": {"content": f"{opportunity.accomp_postcode:05}"}}]
        }
    if opportunity.vo_information is not None:
        properties["VO information"] = {
            "rich_text": [{"text": {"content": opportunity.vo_information}}]
        }
    if opportunity.accomp_datetime is not None and isinstance(
        opportunity.accomp_datetime, datetime
    ):
        properties["Date, time"] = {
            "date": {"start": opportunity.accomp_datetime.strftime("%Y-%m-%d %H:%M:%S")}
        }
    properties["Status"] = {
        "status": {"name": get_clean_select_for_notion(opportunity.status)}
    }
    properties["Opp Type"] = {
        "select": {"name": get_clean_select_for_notion(opportunity.opportunity_type)}
    }
    if opportunity.accomp_translation:
        properties["Translation"] = {
            "multi_select": [
                {"name": get_clean_select_for_notion(opportunity.accomp_translation)}
            ]
        }

    properties["Refugee Languages"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(language)}
            for language in get_list(opportunity.languages.all(), "title")
        ]
    }
    properties["Type"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(activity)}
            for activity in get_list(opportunity.activities.all(), "title")
        ]
    }
    properties["District VO"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(location)}
            for location in get_list(opportunity.berlin_locations.all(), "name")
        ]
    }
    properties["Skills"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(skill)}
            for skill in get_list(opportunity.skills.all(), "title")
        ]
    }
    properties["VO Schedule"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(day)}
            for day in get_schedule_list(opportunity)
        ]
    }

    properties["RAC Contact"] = {
        "rich_text": [
            {
                "text": {
                    "content": comments_delimiter.join(
                        [
                            opportunity.rac_full_name or comments_none,
                            opportunity.rac_email or comments_none,
                            opportunity.rac_phone or comments_none,
                            opportunity.rac_address or comments_none,
                            str(opportunity.rac_plz) or comments_none,
                        ]
                    )
                }
            }
        ]
    }

    properties["Number of volunteers needed"] = {
        "select": {"name": str(opportunity.volunteers_number)}
    }

    if not opportunity.notion_id:
        properties["Timestamp"] = {
            "date": {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        }

    page = notion_handler.add_page(properties=properties)

    opportunity.notion_id = get_key_value(page, ["id"])
    logger.debug(f"Page: {opportunity.notion_id=} is written.")
    opportunity.save()
