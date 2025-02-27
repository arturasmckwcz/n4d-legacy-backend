import json
from pathlib import Path

from django.db import transaction

from data.models import Activity, Language, Opportunity, Skill


def load_opportunities():
    try:
        file_path = Path(__file__).parent / "opportunities.json"
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        with transaction.atomic():
            for opp_data in data["opportunities"]:
                original_language_iso = opp_data.pop("original_language")
                language_codes = opp_data.pop("languages")
                title = opp_data.pop("title")
                vo_information = opp_data.pop("vo_information", None)
                accomp_information = opp_data.pop("accomp_information", None)
                skill_titles = opp_data.pop("skills", [])
                activity_titles = opp_data.pop("activities", [])

                opportunity = Opportunity.create_with_translation(
                    title=title,
                    original_language_iso=original_language_iso,
                    vo_information=vo_information,
                    accomp_information=accomp_information,
                    **opp_data,
                )

                languages = Language.objects.filter(iso_code__in=language_codes)
                opportunity.languages.add(*languages)

                skills = Skill.objects.filter(title__in=skill_titles)
                opportunity.skills.set(skills)

                activities = Activity.objects.filter(title__in=activity_titles)
                opportunity.activities.set(activities)

                print(f"Created opportunity: {opportunity}")

        print("Successfully loaded all sample opportunities!")

    except Exception as e:
        print(f"Error loading sample opportunities: {str(e)}")


# python manage.py shell
# from data.fixtures.generate_data import load_opportunities
# load_opportunities()
