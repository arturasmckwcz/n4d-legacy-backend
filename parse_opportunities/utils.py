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

sample = {
    "Timestamp": "August 9, 2024",
    "Status": "Volunteers Needed",
    "Name": "Support during a summer festival in Lichtenberg",
    "Type": "Festival, One timer",
    "District": "Lichtenberg",
    "Number of volunteers needed": "4",
    "Schedule": "14-18, September 24th",
    "VO information": "Am 24.09 machen wir ein Sommerfest hier in unserer Unterkunft. Daher bin ich auch der Suche nach helfende Hände an dem Tag von 14:00-18:00 für zum Beispiel: Auf und Abbau Tische/ Stühle, Kinderschminken, Hüpburg, Getränke und Popkorn Ausgabe, Tombola, etc…",
    "Accommodation Centre": "Refugium Lichtenberg (https://www.notion.so/Refugium-Lichtenberg-01584531f798456ebd3c99fbe6db7c26?pvs=21)",
    "Volunteers contacted": "",
    "Volunteers active": "",
    ":earth_africa: NGOs": "",
    "Languages needed": "English, German",
    "Target group": "Adults, Kids, Teenagers",
    "Link": "",
    "Related to Volunteers (1) (VO active)": "",
    "Related to Volunteers (1) (VO contacted)": "",
    "Related to Volunteers (1) (VO contacted) 1": "",
    "Related to Volunteers (1) t (VO active)": "",
    "ID": "VOL-136",
}

json_model_key_map = {
    "Status": "opportunity.status",
    "Name": "opportunity.title",
    "Type": "opportunity.activities",
    "District": "opportunity.locations",
    "Number of volunteers needed": "opportunity.volunteers_number",
    "Schedule": "opportunity.timeslots",
    "Accommodation Centre": "opportunity.organization",
    "Languages needed": "opportunity.languages",
    "Target group": "opportunity.target_groups",
    "VO information": "opportunity.vo_information",
    "ID": "opportunity.notion_id",
}
DUMMY = "DUMMY"
lang_DTO = {
    "English": {"iso_code": "en", "level": "advanced"},
    "German": {"iso_code": "de", "level": "advanced"},
    "Arabic": {"iso_code": "ar", "level": "advanced"},
    "Farsi": {"iso_code": "fa", "level": "advanced"},
    "Persian": {"iso_code": "fa", "level": "advanced"},
    "Russian": {"iso_code": "ru", "level": "advanced"},
    "Ukrainian": {"iso_code": "uk", "level": "advanced"},
    "Turkish": {"iso_code": "tr", "level": "advanced"},
    "Spanish": {"iso_code": "es", "level": "advanced"},
}
value_type_field_map = {
    "volunteers_number": "int",
}


def parse_opportunity_json(json_data: list[dict]):
    # 1. do DTO mapping
    for opportunity_json in json_data:
        opportunity = {}
        for key, value in json_model_key_map.items():
            if value:
                model, field = value.split(".")
                if model == "opportunity":
                    opportunity[field] = get_value(field, opportunity_json[key])

        # 2. figure what already existing objects fits or create new ones
        logger.debug(f"{opportunity=}")
        opportunity = parse_opportunity_dict(opportunity)

    return len(json_data)


def parse_opportunity_dict(opportunity_dict: dict) -> Opportunity:
    """
    "Name": "opportunity.title",
    "Accommodation Centre": "opportunity.organization",
    "Target group": "opportunity.target_groups",
    """
    name = opportunity_dict["organization"]
    organization = get_instance(
        opt={"name": name},
        data={
            "name": name,
            "location": get_instance(opt={"title": DUMMY}, model=Location),
            "contact": get_instance(opt={"title": DUMMY}, model=Contact),
        },
        model=Organization,
    )
    del opportunity_dict["organization"]

    target_groups = [
        get_instance(opt={"title": t_g.strip()}, model=TargetGroup)
        for t_g in opportunity_dict["target_groups"].split(",")
    ]

    del opportunity_dict["target_groups"]

    logger.debug(f"{opportunity_dict}")

    # opportunity = Opportunity(**opportunity_dict, organization=organization)

    activities = [
        get_instance(opt={"title": activity.strip()}, model=Activity)
        for activity in opportunity_dict["activities"].split(",")
    ]
    del opportunity_dict["activities"]

    locations = [
        get_instance(opt={"title": location.strip()}, model=Location)
        for location in opportunity_dict["locations"].split(",")
    ]
    del opportunity_dict["locations"]

    timeslots = [
        get_instance(opt={"title": timeslot.strip()}, model=Timeslot)
        for timeslot in opportunity_dict["timeslots"].split(",")
    ]
    del opportunity_dict["timeslots"]

    languages = []
    for language in opportunity_dict["languages"].split(","):
        languages = Language.objects.filter(
            iso_code=get_lang_data(language.strip())["iso_code"]
        )
    del opportunity_dict["languages"]

    opportunity = Opportunity(**opportunity_dict, organization=organization)
    opportunity.save()

    opportunity.activities.set(activities)
    opportunity.locations.set(locations)
    opportunity.timeslots.set(timeslots)
    opportunity.languages.set(languages)
    opportunity.target_groups.set(target_groups)
    opportunity.save()

    logger.debug(f"{opportunity=} {opportunity.__dict__}")
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
        logger.debug(f"created {instance} of {model}")

    return instance


def get_lang_data(lang):
    return (
        lang_DTO[lang]
        if lang and lang in lang_DTO
        else {"iso_code": "ot", "level": "beginner"}
    )


def get_value(field, value):
    if field in value_type_field_map:
        if value_type_field_map[field] == "int":
            if value == "":
                return "0"
            else:
                return value

    return value
