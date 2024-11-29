from datetime import datetime
from typing import List

import structlog
from django.db import transaction

from alfred.notion_handler import NotionHandler
from alfred.utils import (
    YesNo,
    get_clean_select_for_notion,
    get_key_value,
    get_the_first,
    get_yes_no,
    is_later_than,
    parse_yes_no,
    read_env_var,
)
from data.enums import Need4DeedTimeSlots
from data.models import (
    Activity,
    BerlinLocation,
    Language,
    Need4DeedDaySchedule,
    Skill,
    VolunteerForm,
    VolunteerLanguageM2M,
)
from data.utils import get_day_number_from_DAY_CHOICES, is_in_DAY_CHOICES

logger = structlog.get_logger(__name__)

notion_database_id = read_env_var("NOTION_VOLUNTEERS_ID")
notion_handler = NotionHandler(notion_database_id)


full_name_placeholder = "NAME PLACEHOLDER"


def update_notion_page(handler, page_id, properties):
    return handler.update_page(page_id, properties)


def execute_volunteerform_seed_pipeline():
    volunteers_from_notion = notion_handler.get_database_data()
    logger.info(f"Found {len(volunteers_from_notion)} rows in Volunteers")

    for volunteer_page in volunteers_from_notion:
        write_or_update_page_to_db(volunteer_page=volunteer_page)


def execute_volunteerform_pipeline():
    volunteers_from_notion = notion_handler.get_database_data()
    logger.info(f"Found {len(volunteers_from_notion)} rows in Volunteers")

    # 1. select updated in the Notion table and update db
    count = 0
    for volunteer_page in volunteers_from_notion:
        volunteerform_object = get_database_object(volunteer_page)
        if volunteerform_object and is_later_than(
            datetime.fromisoformat(volunteer_page["last_edited_time"]),
            volunteerform_object.updated_at,
        ):
            count += 1
            write_or_update_page_to_db(
                update_object=volunteerform_object, volunteer_page=volunteer_page
            )
    logger.info(f"Updated {count} VolunteerForm objects")

    # 2. notion pages to be deleted from db
    notion_ids = [volunteer_page["id"] for volunteer_page in volunteers_from_notion]
    volunteerform_objects = (
        VolunteerForm.objects.filter()
        .exclude(notion_id__in=notion_ids)
        .exclude(notion_id=None)
    )
    logger.info(
        f"Attempting to remove {len(volunteerform_objects)} VolunteerForm objects"
    )
    volunteerform_objects.all().delete()

    # 3. select new records in the DB and create new rows in the Notion table
    new_volunteerform_objects = VolunteerForm.objects.filter(notion_id=None).all()
    logger.info(f"Found {len(new_volunteerform_objects)} new VolunteerForm objects.")
    for new_volunteerform in new_volunteerform_objects:
        write_volunteerform_to_notion(new_volunteerform)


def prepare_page_data_for_db(volunteer_page: dict) -> tuple | None:
    volunteer_form_data = {}
    try:
        volunteer_form_data["notion_id"] = volunteer_page["id"]

        email = get_the_first(
            volunteer_page["properties"]["E-mail"]["title"], should_raise=True
        )
        volunteer_form_data["email"] = get_key_value(email, ["text", "content"])

        full_name = volunteer_page["properties"]["Name"]["select"]
        full_name = get_key_value(full_name, ["name"])
        volunteer_form_data["full_name"] = full_name or full_name_placeholder

        phone = get_the_first(volunteer_page["properties"]["Phone Number"]["rich_text"])
        phone = get_key_value(phone, ["plain_text"])
        volunteer_form_data["phone"] = phone or None

        postal_code = get_key_value(
            volunteer_page, ["properties", "Post code", "number"]
        )
        volunteer_form_data["postal_code"] = postal_code or 0

        volunteer_form_data["good_conduct_certificate"] = get_key_value(
            volunteer_page,
            ["properties", "Certificate of good conduct", "select", "name"],
        )

        volunteer_form_data["if_measles_vaccination"] = parse_yes_no(
            get_key_value(
                volunteer_page, ["properties", "Measles vacc", "select", "name"]
            )
        )

        lead_from = get_key_value(
            volunteer_page,
            ["properties", "Where did you hear", "multi_select"],
            null=[],
        )
        lead_from = ", ".join([lead["name"] for lead in lead_from])
        volunteer_form_data["lead_from"] = lead_from or None

        comments_delimiter = "<|>"
        comments_none = "NONE"
        # the order: "Comments","Other comments on schedule","Other activities","Other languages"
        comments_just = get_the_first(
            volunteer_page["properties"]["Comments"]["rich_text"]
        )
        comments_just = get_key_value(comments_just, ["plain_text"]) or comments_none
        comments_schedule = get_the_first(
            volunteer_page["properties"]["Other comments on schedule"]["rich_text"]
        )
        comments_schedule = (
            get_key_value(comments_schedule, ["plain_text"]) or comments_none
        )
        comments_activities = get_the_first(
            volunteer_page["properties"]["Other activities"]["rich_text"]
        )
        comments_activities = (
            get_key_value(comments_activities, ["plain_text"]) or comments_none
        )
        comments_languages = get_the_first(
            volunteer_page["properties"]["Other languagues"]["rich_text"]
        )
        comments_languages = (
            get_key_value(comments_languages, ["plain_text"]) or comments_none
        )
        volunteer_form_data["comments"] = (
            comments_just
            + comments_delimiter
            + comments_schedule
            + comments_delimiter
            + comments_activities
            + comments_delimiter
            + comments_languages
        )[:1024]

        # the order: "Status","Coordinator Comments","VO contacted","VO active","Days"
        comments_status = get_the_first(
            volunteer_page["properties"]["Status"]["multi_select"]
        )
        comments_status = get_key_value(comments_status, ["name"]) or comments_none
        comments_coordinator = get_the_first(
            volunteer_page["properties"]["Coordinator Comments"]["rich_text"]
        )
        comments_coordinator = (
            get_key_value(comments_coordinator, ["plain_text"]) or comments_none
        )
        comments_vo_contacted = get_key_value(
            volunteer_page, ["properties", "VO contacted", "relation"], null=[]
        )
        comments_vo_contacted = (
            ",".join(vo["id"] for vo in comments_vo_contacted)
            if comments_vo_contacted
            else comments_none
        )
        comments_vo_active = get_key_value(
            volunteer_page, ["properties", "VO active", "relation"], null=[]
        )
        comments_vo_active = (
            ",".join(vo["id"] for vo in comments_vo_active)
            if comments_vo_active
            else comments_none
        )
        comments_days = get_key_value(
            volunteer_page, ["properties", "Days", "select"], null=[]
        )
        comments_days = (
            ",".join(day["name"] for day in comments_days)
            if comments_days
            else comments_none
        )
        volunteer_form_data["comments_workflow"] = (
            comments_coordinator
            + comments_delimiter
            + comments_status
            + comments_delimiter
            + comments_vo_contacted
            + comments_delimiter
            + comments_days
        )[:1024]

    except Exception as e:
        logger.error(
            f"Error {repr(e)} occurred while processing Notion page id={volunteer_page['id']} structure. Skipping."
        )
        return None

    m2m_data = {}

    # 2 add add locations
    locations = []
    for location_in_page in volunteer_page["properties"][
        "Preferred Volunteering Locations"
    ]["multi_select"]:
        locations.append(location_in_page["name"])
    m2m_data["locations"] = locations

    # 3 add languages
    languages = []
    for language_in_page in volunteer_page["properties"]["Languages"]["multi_select"]:
        language = language_in_page["name"].split(" ")
        if len(language) != 2:
            continue
        languages.append(language)
    m2m_data["languages"] = languages

    # 4 add schedule
    schedule = [
        get_key_value(day, ["name"])
        for day in (
            get_key_value(volunteer_page, ["properties", "Days", "multi_select"]) or []
        )
    ]
    m2m_data["schedule"] = schedule

    # 5 add activities and skills
    activities = []
    for activity_in_page in volunteer_page["properties"]["Activities"]["multi_select"]:
        activities.append(activity_in_page["name"])
    m2m_data["activities"] = activities

    skills = []
    for skill_in_page in volunteer_page["properties"]["Skills"]["multi_select"]:
        skills.append(skill_in_page["name"])
    m2m_data["skills"] = skills

    return (volunteer_form_data, m2m_data)


# PostgresQL doesn't support nested transactions, so we needed combining update/create
# in order to roll back deletion if creation fails
def write_or_update_page_to_db(
    volunteer_page: dict, update_object: VolunteerForm | None = None
):
    data = prepare_page_data_for_db(volunteer_page)
    if not data:
        return

    volunteer_form_data, m2m_data = data

    try:
        with transaction.atomic():
            if update_object:
                success, deleted_dict = update_object.delete()

            volunteerform_object = VolunteerForm(**volunteer_form_data)
            volunteerform_object.save()

            # 2 add add locations
            location_objects = []
            for location in m2m_data["locations"]:
                try:
                    location_object, _ = BerlinLocation.objects.get_or_create(
                        name=location
                    )
                    location_objects.append(location_object)
                except Exception as e:
                    logger.error(
                        f"Error {e} occurred while processing location {location=}"
                    )
            volunteerform_object.preferred_berlin_locations.set(location_objects)

            # 3 add languages
            for language in m2m_data["languages"]:
                title, level = language

                if title == "Farsi/Dari" or title == "Farsi":
                    title = "Persian"

                language_object = Language.objects.filter(title=title).first()
                if language_object:
                    VolunteerLanguageM2M.objects.create(
                        language=language_object,
                        volunteerform=volunteerform_object,
                        level=level,
                    )

            # 4 add schedule
            schedule_objects = parse_days(m2m_data["schedule"])
            if schedule_objects is None:
                update_notion_page(
                    handler=notion_handler,
                    page_id=volunteer_page["id"],
                    properties={
                        "Schedule okay": {
                            "select": {"name": YesNo.NO.capitalize()},
                        },
                    },
                )
            else:
                volunteerform_object.schedule.set(schedule_objects)

            # 5 add activities and skills
            activity_objects = []
            for activity in m2m_data["activities"]:
                try:
                    activity_object, _ = Activity.objects.get_or_create(title=activity)
                    activity_objects.append(activity_object)
                except Exception as e:
                    logger.error(
                        f"Error {e} occurred while processing activity {activity=}"
                    )
            volunteerform_object.activities.set(activity_objects)
            skill_objects = []
            for skill in m2m_data["skills"]:
                try:
                    skill_object, _ = Skill.objects.get_or_create(title=skill)
                    skill_objects.append(skill_object)
                except Exception as e:
                    logger.error(f"Error {e} occurred while processing skill {skill=}")
            volunteerform_object.skills.set(skill_objects)
    except Exception as e:
        logger.error(
            f"Error {repr(e)} occurred while writing Notion page id={volunteer_page['id']} to database. Skipping."
        )
        return


def parse_days(days: List[str] | None) -> List[Need4DeedDaySchedule] | None:
    if (days is None) and (not isinstance(days, list)):
        return None

    schedule_objects = []

    for day in days:
        day, *timeframes = day.split(" ")
        if not is_in_DAY_CHOICES(day):
            continue

        timeframes = " ".join(timeframes)
        for form_timeframe, _ in Need4DeedTimeSlots.choices:
            if form_timeframe in timeframes:
                schedule_object, _ = Need4DeedDaySchedule.objects.get_or_create(
                    day=get_day_number_from_DAY_CHOICES(day),
                    time_slot=form_timeframe,
                )
                schedule_objects.append(schedule_object)

    return schedule_objects or None


def get_database_object(volunteer_page: dict) -> VolunteerForm | None:
    try:
        return VolunteerForm.objects.get(notion_id=volunteer_page["id"])
    except VolunteerForm.DoesNotExist:
        return None


def write_volunteerform_to_notion(volunteerform: VolunteerForm):
    properties = {}
    properties["E-mail"] = {
        "title": [{"text": {"content": volunteerform.email, "link": None}}]
    }
    properties["Name"] = {
        "select": {"name": get_clean_select_for_notion(volunteerform.full_name)}
    }
    properties["Phone Number"] = {
        "rich_text": [{"text": {"content": volunteerform.phone}}]
    }
    properties["Post code"] = {"number": volunteerform.postal_code}
    properties["Preferred Volunteering Locations"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(location)}
            for location in get_list(
                volunteerform.preferred_berlin_locations.all(), "name"
            )
        ]
    }
    properties["Languages"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(language)}
            for language in get_language_list(volunteerform)
        ]
    }
    properties["Days"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(day)}
            for day in get_schedule_list(volunteerform)
        ]
    }
    properties["Schedule okay"] = {"select": {"name": "Yes"}}
    properties["Activities"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(activity)}
            for activity in get_list(volunteerform.activities.all(), "title")
        ]
    }
    properties["Skills"] = {
        "multi_select": [
            {"name": get_clean_select_for_notion(skill)}
            for skill in get_list(volunteerform.skills.all(), "title")
        ]
    }
    properties["Certificate of good conduct"] = {
        "select": {
            "name": get_clean_select_for_notion(volunteerform.good_conduct_certificate)
            or YesNo.NO
        }
    }
    properties["Measles vacc"] = {
        "select": {"name": get_yes_no(volunteerform.if_measles_vaccination)}
    }
    properties["Where did you hear"] = {
        "multi_select": (
            [
                {"name": get_clean_select_for_notion(source)}
                for source in volunteerform.lead_from.split(", ")
            ]
            if volunteerform.lead_from
            else []
        )
    }
    properties["Comments"] = {
        "rich_text": [{"text": {"content": volunteerform.comments}}]
    }
    opportunity_page_id = (
        str(volunteerform.origin_opportunity.notion_id)
        if volunteerform.origin_opportunity
        else None
    )
    if opportunity_page_id:
        properties["Opportunity link"] = {"relation": [{"id": opportunity_page_id}]}
    if not volunteerform.notion_id:
        properties["Timestamp"] = {
            "date": {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        }

    page = notion_handler.add_page(properties=properties)

    volunteerform.notion_id = get_key_value(page, ["id"])
    logger.debug(f"Page: {volunteerform.notion_id=} is written.")
    volunteerform.save()


def get_language_list(volunteer: VolunteerForm) -> list[str]:
    languages_and_levels = []
    for language in volunteer.languages.all():
        try:
            language_level = VolunteerLanguageM2M.objects.filter(
                language=language, volunteerform=volunteer
            ).first()
            if language_level:
                languages_and_levels.append(
                    f"{language.title.capitalize()} {language_level.level.capitalize() if language_level.level else None}"
                )
        except VolunteerLanguageM2M.DoesNotExist:
            logger.error(
                f"VolunteerLanguageM2M.DoesNotExist raised for language {language}"
            )

    return languages_and_levels


def get_schedule_list(volunteer: VolunteerForm, delimiter=" | ") -> list[str]:
    days = [
        "Occasional",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    schedule = {}
    for item in volunteer.schedule.all():
        day = item.day
        time_slot = item.time_slot
        if day in schedule:
            schedule[day].append(time_slot)
        else:
            schedule[day] = [time_slot]

    return [f"{days[day]} {delimiter.join(schedule[day])}" for day in schedule.keys()]


def get_list(items, key: str) -> list[str]:
    return [getattr(item, key) for item in items]
