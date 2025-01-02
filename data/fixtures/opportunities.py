import json
from datetime import datetime, timezone

new_opportunity = {"model": "data.opportunity"}
new_translation = {"model": "data.opportunitytranslation"}
opportunities_loaddata = []
model_fields = [
    "opportunity_type",
    "schedule_str",
    "datetime_str",
    "status",
    "accomp_datetime",
]

with open("opportunities_get.json", "r") as f:
    opportunities_get = json.load(f)

with open("activities.json", "r") as f:
    activities = json.load(f)

with open("berlinlocations.json", "r") as f:
    berlinlocations = json.load(f)

with open("languages.json", "r") as f:
    languages = json.load(f)

with open("need4deeddayschedule.json", "r") as f:
    need4deeddayschedule = json.load(f)

with open("skills.json", "r") as f:
    skills = json.load(f)


def get_pk_by_key_value(data_list, key_value_list):
    pk = None
    for item in data_list:
        flag = True
        for key, value in key_value_list:
            flag = flag and item["fields"][key] == value
        if flag:
            pk = item["pk"]
            break
    return pk


opportunity_pk = 0
translation_pk = 0
language_de_pk = get_pk_by_key_value(languages, [("iso_code", "de")])

for opportunity_get in opportunities_get:
    # 1. init Opportunity model
    opportunity_pk += 1
    opportunity_loaddata = {"pk": opportunity_pk}
    opportunity_loaddata.update(new_opportunity)
    opportunity_loaddata["fields"] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # 2. fill model fields
    for model_field in model_fields:
        opportunity_loaddata["fields"][model_field] = opportunity_get[model_field]

    # 3. fill m2m fields
    berlinlocations_loaddata = []
    for location_get in opportunity_get["berlin_locations"]:
        pk = get_pk_by_key_value(berlinlocations, [("name", location_get["name"])])
        if pk:
            berlinlocations_loaddata.append(pk)
    opportunity_loaddata["fields"]["berlin_locations"] = berlinlocations_loaddata

    timeslots_loaddata = []
    for timeslot_get in opportunity_get["timeslots"]:
        pk = get_pk_by_key_value(
            need4deeddayschedule,
            [("day", timeslot_get["day"]), ("time_slot", timeslot_get["time_slot"])],
        )
        if pk:
            timeslots_loaddata.append(pk)
    opportunity_loaddata["fields"]["timeslots"] = timeslots_loaddata

    activities_loaddata = []
    for activity_get in opportunity_get["activities"]:
        pk = get_pk_by_key_value(activities, [("title", activity_get["title"])])
        if pk:
            activities_loaddata.append(pk)
    opportunity_loaddata["fields"]["activities"] = activities_loaddata

    languages_loaddata = []
    for language_get in opportunity_get["languages"]:
        pk = get_pk_by_key_value(languages, [("title", language_get["title"])])
        if pk:
            languages_loaddata.append(pk)
    opportunity_loaddata["fields"]["languages"] = languages_loaddata

    skills_loaddata = []
    for skill_get in opportunity_get["skills"]:
        pk = get_pk_by_key_value(skills, [("title", skill_get["title"])])
        if pk:
            skills_loaddata.append(pk)
    opportunity_loaddata["fields"]["skills"] = skills_loaddata

    opportunities_loaddata.append(opportunity_loaddata)

    # 4. init OpportunityTranslation module
    translation_pk += 1
    translations_loaddata = {"pk": translation_pk}
    translations_loaddata.update(new_translation)
    translations_loaddata["fields"] = {}

    # 5. set translation object
    translations_loaddata["fields"]["title"] = opportunity_get["title"]
    translations_loaddata["fields"]["accomp_information"] = opportunity_get[
        "accomp_information"
    ]
    translations_loaddata["fields"]["vo_information"] = opportunity_get[
        "vo_information"
    ]
    translations_loaddata["fields"]["opportunity"] = opportunity_pk
    translations_loaddata["fields"]["language"] = language_de_pk

    opportunities_loaddata.append(translations_loaddata)

with open("opportunities.json", "w") as f:
    json.dump(opportunities_loaddata, f, indent=4)
