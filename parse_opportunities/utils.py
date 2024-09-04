import structlog
from django.core.exceptions import ObjectDoesNotExist

from data.models import (
    Activity,
    Contact,
    Language,
    Location,
    Opportunity,
    Organization,
    TargetGroup,
    Timeslot,
)

logger = structlog.get_logger(__name__)

DUMMY = "DUMMY"


def parse_opportunity_json(json_data: list[dict]):
    json_model_key_map = {
        "Status": "opportunity.status",
        "Name": "opportunity.title",
        "Type": "opportunity.activities",
        "Appointment Type": "opportunity.activities",
        "District": "opportunity.locations",
        "District (Appointment)": "opportunity.locations",
        "Number of volunteers needed": "opportunity.volunteers_number",
        "Schedule": "opportunity.timeslots",
        "Date": "opportunity.timeslots",
        "Accommodation Centre": "opportunity.organization",
        "🏢 Refugee Accommodation Centres": "opportunity.organization",
        "Languages needed": "opportunity.languages",
        "Refugee Language": "opportunity.languages",
        "Translation Language": "opportunity.translate_languages",
        "Target group": "opportunity.target_groups",
        "VO information": "opportunity.vo_information",
        "ID": "opportunity.notion_id",
    }
    # 1. do DTO mapping
    for opportunity_json in json_data:
        opportunity = {}
        for attribute in opportunity_json:
            if attribute in json_model_key_map:
                model, field = json_model_key_map[attribute].split(".")
                if model == "opportunity":
                    opportunity[field] = get_value(field, opportunity_json[attribute])

        # 2. figure what already existing objects fits or create new ones
        logger.debug(f"opportunity: {opportunity}")
        opportunity = parse_opportunity_dict(opportunity)

    return len(json_data)


def parse_opportunity_dict(opportunity_dict: dict) -> Opportunity:
    """
    "Name": "opportunity.title",
    "Accommodation Centre": "opportunity.organization",
    "Target group": "opportunity.target_groups",
    """
    name = opportunity_dict["organization"]
    organization = (
        get_instance(
            opt={"name": name},
            data={
                "name": name,
                "location": get_instance(opt={"title": DUMMY}, model=Location),
                "contact": get_instance(opt={"title": DUMMY}, model=Contact),
            },
            model=Organization,
        )
        if name is not None
        else None
    )
    del opportunity_dict["organization"]

    if "target_groups" in opportunity_dict:
        target_groups = [
            get_instance(opt={"title": t_g.strip()}, model=TargetGroup)
            for t_g in opportunity_dict["target_groups"].split(",")
        ]
        del opportunity_dict["target_groups"]
    else:
        target_groups = []

    if "activities" in opportunity_dict:
        activities = [
            get_instance(opt={"title": activity.strip()}, model=Activity)
            for activity in opportunity_dict["activities"].split(",")
        ]
        del opportunity_dict["activities"]
    else:
        activities = []

    if "locations" in opportunity_dict:
        locations = [
            get_instance(opt={"title": location.strip()[:32]}, model=Location)
            for location in opportunity_dict["locations"].split(",")
        ]
        del opportunity_dict["locations"]
    else:
        locations = []

    if "timeslots" in opportunity_dict:
        timeslots = [
            get_instance(opt={"title": timeslot.strip()}, model=Timeslot)
            for timeslot in opportunity_dict["timeslots"].split(",")
        ]
        del opportunity_dict["timeslots"]
    else:
        timeslots = []

    languages = []
    if "languages" in opportunity_dict:
        for language in opportunity_dict["languages"].split(","):
            try:
                lang_data = get_lang_data(language.strip())
                lang_objs = Language.objects.filter(**lang_data)
                languages.extend(lang_objs)
            except Language.DoesNotExist:
                pass
        del opportunity_dict["languages"]

    translate_languages = []
    if "translate_languages" in opportunity_dict:
        for language in opportunity_dict["translate_languages"].split(","):
            try:
                lang_data = get_lang_data(language.strip())
                lang_objs = Language.objects.filter(**lang_data)
                translate_languages.extend(lang_objs)
            except Language.DoesNotExist:
                pass
        del opportunity_dict["translate_languages"]

    opportunity = Opportunity(
        **opportunity_dict,
        organization=organization,
    )
    opportunity.save()

    opportunity.activities.set(activities)
    opportunity.locations.set(locations)
    opportunity.timeslots.set(timeslots)
    opportunity.languages.set(languages)
    opportunity.translate_languages.set(translate_languages)
    opportunity.target_groups.set(target_groups)
    opportunity.save()

    return opportunity


def get_instance(model, opt, data=None):
    data = data if data else opt
    for key in data:
        if not data[key]:
            data[key] = DUMMY
            opt[key] = DUMMY
    try:
        instance = model.objects.get(**opt)
    except ObjectDoesNotExist:
        instance = model(**data)
        instance.save()
        logger.debug(f"created! {instance} of {model}")

    return instance


def get_lang_data(lang):
    lang_DTO = {
        "English": {"iso_code": "en", "level": "fluent"},
        "German": {"iso_code": "de", "level": "fluent"},
        "Arabic": {"iso_code": "ar", "level": "fluent"},
        "Farsi": {"iso_code": "fa", "level": "fluent"},
        "Persian": {"iso_code": "fa", "level": "fluent"},
        "Russian": {"iso_code": "ru", "level": "fluent"},
        "Ukrainian": {"iso_code": "uk", "level": "fluent"},
        "Turkish": {"iso_code": "tr", "level": "fluent"},
        "Spanish": {"iso_code": "es", "level": "fluent"},
        "default": {"iso_code": "ot", "level": "fluent"},
    }

    return lang_DTO[lang] if lang in lang_DTO else lang_DTO["default"]


def get_value(field, value):
    value_type_field_map = {
        "volunteers_number": "int",
    }

    if field in value_type_field_map:
        if value_type_field_map[field] == "int":
            if value == "":
                return "0"
            else:
                return value

    return value
