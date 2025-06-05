import traceback
from datetime import datetime

import structlog
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from alfred.config.globals import comments_delimiter, comments_none
from alfred.notion_handler import NotionHandler
from alfred.utils import (
    YesNo,
    get_clean_select_for_notion,
    get_database_object,
    get_key_value,
    get_list,
    get_schedule_list,
    get_the_first,
    is_later_than,
    parse_days,
    read_env_var,
    update_notion_page,
)
from data.models import (
    Activity,
    BerlinLocation,
    Language,
    Opportunity,
    OpportunityTranslation,
    Skill,
    TitleTranslation,
)

logger = structlog.get_logger(__name__)

notion_database_id = read_env_var("NOTION_OPPORTUNITIES_ID")
notion_handler = NotionHandler(notion_database_id)


def add_languages_to_opportunity(languages, opportunity_obj):  # 8
    if len(languages) == 0:
        logger.warn(f"No languages to add! {languages=}")
        return

    languages_to_add = []
    for language in languages:
        match language:
            case "Farsi":
                language = "Persian"
            case "Romanes":
                language = "Romany"
            case "Any" | "no specific language needed" | "No specific language needed":
                continue

        language_obj = Language.objects.filter(title=language).first()
        languages_to_add.append(language_obj)
    try:
        opportunity_obj.languages.set(languages_to_add)
    except Exception:
        logger.error(f"{opportunity_obj} has incompatible language")


def prepare_opportunity_data_for_db(opportunity_page: dict) -> tuple | None:  # 9
    opportunity_data = {}
    translation_data = {}
    notion_id = get_key_value(opportunity_page, ["id"])
    try:
        opportunity_data["notion_id"] = notion_id
        opportunity_data["last_edited_time_notion"] = opportunity_page[
            "last_edited_time"
        ]

        title_from_notion = get_the_first(
            opportunity_page["properties"]["Name"]["title"],
            should_raise=True,
            list_name="Name title",
        )
        translation_data["title"] = get_key_value(
            title_from_notion, ["text", "content"], should_raise=True
        )

        voInfo = get_the_first(
            opportunity_page["properties"]["VO information"]["rich_text"]
        )
        translation_data["vo_information"] = get_key_value(voInfo, ["plain_text"])

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
        translation_data["accomp_information"] = get_key_value(aaInfo, ["plain_text"])

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

        if opportunity_page["properties"].get("Translation"):
            aaTranslate = get_the_first(
                opportunity_page["properties"]["Translation"]["multi_select"]
            )
            opportunity_data["accomp_translation"] = get_key_value(
                aaTranslate, ["name"]
            )

        opportunity_type = get_key_value(
            opportunity_page, ["properties", "Opp Type", "select", "name"]
        )
        if opportunity_type == "":
            logger.error(
                f"Opportunity {notion_id=} has incorrect opportunity type {opportunity_type=}"
            )
            raise ValueError

        opportunity_data["opportunity_type"] = opportunity_type

        opportunity_data["status"] = get_key_value(
            opportunity_page, ["properties", "Status", "status", "name"]
        )

        volunteers_number = get_key_value(
            opportunity_page,
            ["properties", "Number of volunteers needed", "select", "name"],
        )
        if volunteers_number:
            opportunity_data["volunteers_number"] = int(volunteers_number)
        else:
            opportunity_data["volunteers_number"] = 0

        opportunity_data["schedule_str"] = ", ".join(
            [
                get_key_value(timeslot, ["name"])
                for timeslot in get_key_value(
                    opportunity_page, ["properties", "VO Schedule", "multi_select"]
                )
            ]
        )

        rac_info = get_the_first(
            opportunity_page["properties"]["RAC Contact"]["rich_text"]
        )
        rac_info = get_key_value(rac_info, ["plain_text"])
        if isinstance(rac_info, str):
            rac_info = (
                rac_info.split(comments_delimiter) if isinstance(rac_info, str) else []
            )
            if len(rac_info) == 5:
                rac_full_name, rac_email, rac_phone, rac_address, rac_plz = rac_info
                opportunity_data["rac_full_name"] = rac_full_name
                opportunity_data["rac_email"] = rac_email
                opportunity_data["rac_phone"] = rac_phone
                opportunity_data["rac_address"] = rac_address
                opportunity_data["rac_plz"] = rac_plz
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(
            f"Error {repr(e)} occurred while preparing model fields by Notion page {notion_id=}. Skipping. \n{tb}"
        )
        raise

    def get_multi_select_from_page(key: str, should_raise=False) -> list:
        items = get_key_value(opportunity_page, ["properties", key, "multi_select"])
        if isinstance(items, list):
            return [item["name"] for item in items]
        elif should_raise:
            raise ValueError(f'Value of "{key}" column is not a list {notion_id=}')
        else:
            return []  # TODO: add logging

    m2m_data = {}

    for field, column in [
        ("languages", "Refugee Languages"),
        ("activities", "Type"),
        ("berlin_locations", "District VO"),
        ("skills", "Skills"),
        ("timeslots", "VO Schedule"),
    ]:
        m2m_data[field] = get_multi_select_from_page(column)

    return (
        opportunity_data,
        m2m_data,
        translation_data,
    )


def write_or_update_opportunity_to_db(  # 5
    opportunity_page: dict, update_object: Opportunity | None = None
):
    data = prepare_opportunity_data_for_db(opportunity_page)  # 6

    if not data:
        return

    opportunity_data, m2m_data, translation_data = data

    logger.info(
        f"Attempting to write or update opportunity to db {opportunity_data['notion_id']=}"
    )
    try:
        with transaction.atomic():
            if update_object:
                deleted = update_object.delete()
            else:
                deleted = None

            logger.debug(f"Attempting to delete objects: {deleted=}")

            # 1. create model

            opportunity_object = Opportunity(**opportunity_data)

            # 1.1. add "de" as original_language
            opportunity_object.original_language = Language.get_language_obj("de")
            opportunity_object.save()
            logger.debug(
                f"{opportunity_object.rac_email=}, {opportunity_object.notion_id=}"
            )

            # 2. add M2Ms

            if not m2m_data:
                logger.info(f"No m2m data for {opportunity_data['notion_id']=}")
                return

            add_languages_to_opportunity(m2m_data["languages"], opportunity_object)  # 7

            berlin_location_objects = []
            for location in m2m_data["berlin_locations"]:
                try:
                    location_object, _ = BerlinLocation.objects.get_or_create(
                        name=location
                    )
                    berlin_location_objects.append(location_object)
                except Exception as e:
                    logger.error(
                        f"Error {e} occurred while processing berlin_location {location=}"
                    )
            opportunity_object.berlin_locations.set(berlin_location_objects)

            activity_objects = []
            content_type_activity = ContentType.objects.get_for_model(Activity)
            for activity in m2m_data["activities"]:
                try:
                    translation_obj = TitleTranslation.objects.filter(
                        translation=activity,
                        content_type=content_type_activity,
                    ).first()
                    if translation_obj:
                        activity_object = Activity.objects.get(
                            pk=translation_obj.object_id
                        )
                        activity_objects.append(activity_object)
                except Exception as e:
                    logger.error(
                        f"Error {e} occurred while processing activity {activity}"  # TODO: add more details
                    )
            opportunity_object.activities.set(activity_objects)

            skill_objects = []
            content_type_skill = ContentType.objects.get_for_model(Skill)
            for skill in m2m_data["skills"]:
                try:
                    translation_obj = TitleTranslation.objects.filter(
                        translation=skill,
                        content_type=content_type_skill,
                    ).first()
                    if translation_obj:
                        skill_object = Skill.objects.get(pk=translation_obj.object_id)
                        skill_objects.append(skill_object)
                except Exception as e:
                    logger.error(
                        f"Error {e} occurred while processing skill {skill=}"
                    )  # TODO: add more details
            opportunity_object.skills.set(skill_objects)

            timeslot_objects = parse_days(m2m_data["timeslots"])
            if timeslot_objects is None:
                update_notion_page(
                    handler=notion_handler,
                    page_id=opportunity_page["id"],
                    properties={
                        "Schedule okay": {
                            "select": {"name": YesNo.NO.capitalize()},
                        },
                    },
                )
            else:
                opportunity_object.timeslots.set(timeslot_objects)

            title_de = translation_data["title"]
            vo_information_de = translation_data["vo_information"]
            accomp_information_de = translation_data["accomp_information"]

            OpportunityTranslation.objects.create(
                opportunity=opportunity_object,
                language=Language.objects.get(iso_code="de"),
                title=title_de,
                vo_information=vo_information_de,
                accomp_information=accomp_information_de,
            )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(
            f"Error {repr(e)} occurred while writing Notion page id={opportunity_page['id']} to database. Skipping.\n{tb}"
        )
        raise


def execute_opportunities_seed_pipeline():  # 10
    # 1. fetch opportunities from Notion
    opportunities_from_notion = notion_handler.get_database_data()
    logger.info("Executing opportunities seed pipeline")
    logger.info(
        f"Found {len(opportunities_from_notion)} rows in Opportunities from Notion"
    )

    # 2. write Notion pages to the database
    count_created = 0
    for opportunity_page in opportunities_from_notion:
        try:
            write_or_update_opportunity_to_db(opportunity_page=opportunity_page)
            count_created += 1
        except Exception as e:
            logger.error(
                f"Error writing opportunity {opportunity_page['id']}: {str(e)}"
            )

    logger.info(f"Created {count_created} Opportunity objects")


def execute_opportunities_sync_pipeline():  # 1
    logger.info("Executing opportunities sync pipeline")
    notion_database_id = read_env_var("NOTION_OPPORTUNITIES_ID")
    notion_handler = NotionHandler(notion_database_id)
    opportunities_from_notion = notion_handler.get_database_data()
    logger.info(
        f"Found {len(opportunities_from_notion)} rows in Opportunities in Notion"
    )
    # 1. select updated in the Notion table and update db
    count_updated = 0
    for opportunity_page in opportunities_from_notion:
        try:
            opportunity_object = get_database_object(opportunity_page, Opportunity)
            if opportunity_object and is_later_than(
                datetime.fromisoformat(opportunity_page["last_edited_time"]),
                opportunity_object.updated_at,
            ):
                # if opportunity_object it means that it exists in the DB and in Notion
                write_or_update_opportunity_to_db(  # 2
                    update_object=opportunity_object, opportunity_page=opportunity_page
                )
                count_updated += 1
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(
                f"Notion record {opportunity_page['id']} resulted in {e} \n{tb}"
            )

    logger.info(f"Updated {count_updated} Opportunity objects")

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
    logger.info(
        f"Found trough filtering {len(new_opportunity_objects)} new Opportunity objects."
    )
    logger.info("Attempting to write opportunities to Notion")
    written_opportunities_to_notion_count = 0
    for new_opportunity in new_opportunity_objects:
        write_opportunity_to_notion(new_opportunity)  # 3
        written_opportunities_to_notion_count += 1
    logger.info(
        f"Should write {written_opportunities_to_notion_count} opportunities to Notion"
    )


def write_opportunity_to_notion(opportunity: Opportunity):  # 4
    properties = {}
    properties["Name"] = {
        "title": [{"text": {"content": opportunity.get_title(), "link": None}}]
    }
    vo_information = opportunity.get_vo_information()
    if vo_information is not None:
        properties["VO information"] = {
            "rich_text": [{"text": {"content": vo_information}}]
        }
    accomp_information = opportunity.get_accomp_information()
    if accomp_information is not None:
        properties["AA Information"] = {
            "rich_text": [{"text": {"content": accomp_information}}]
        }

    if opportunity.accomp_address is not None:
        properties["Address"] = {
            "rich_text": [{"text": {"content": opportunity.accomp_address}}]
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
            for activity in get_list(
                opportunity.activities.all(), "translated_title_de"
            )
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
            for skill in get_list(opportunity.skills.all(), "translated_title_de")
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
    notion_id = get_key_value(page, ["id"])

    opportunity.notion_id = notion_id
    opportunity.save()

    logger.debug(f"Page {notion_id=} is written.")
