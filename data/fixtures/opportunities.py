import json

with open("opportunities_raw.json", "r") as f:
    opportunities = json.load(f)


for opportunity in opportunities:
    del opportunity["fields"]["target_groups"]
    del opportunity["fields"]["translate_languages"]
    opportunity["fields"]["opportunity_type"] = "Volunteering"


with open("opportunities.json", "w") as f:
    json.dump(opportunities, f, indent=4)
