from datetime import datetime, timedelta

from django.utils import timezone
from recurrence import MO, MONTHLY, SA, WEEKLY, Recurrence, Rule

from data.enums import LangLevels, Languages, PayloadType

dtend = timezone.now() + timedelta(days=365)

location_Helter_Skelter = {
    "title": "Gotham RAC",
    "street_address": "Outskirt Strasse 420",
    "post_code": "99007",
    "city": "Gotham",
    "country": "USA",
}
location_USSR = {
    "title": "USSR",
    "street_address": "Hölle Platz 1",
    "post_code": "00666",
    "city": "Moscow",
    "country": "USSR",
}

languages = [
    {"iso_code": Languages.GERMAN, "level": LangLevels.BEGINNER},
    {"iso_code": Languages.ENGLISH, "level": LangLevels.ADVANCED},
    {"iso_code": Languages.RUSSIAN, "level": LangLevels.FLUENT},
]

activities = [
    {"title": "Daycare"},
    {"title": "Translation"},
    {"title": "Sports"},
]

skills = [
    {"title": "Music"},
    {"title": "Football"},
    {"title": "Teaching"},
]

timeslots = [
    {
        "start": timezone.make_aware(datetime(2024, 10, 7, 8, 0, 0, 0)),
        "end": timezone.make_aware(datetime(2024, 10, 7, 8, 0, 0, 0)),
        "recurrence": Recurrence(rrules=[Rule(freq=WEEKLY, wkst=MO)], dtend=dtend),
    },
    {
        "start": timezone.make_aware(datetime(2024, 7, 27, 12, 0, 0, 0)),
        "end": timezone.make_aware(datetime(2024, 7, 27, 14, 0, 0, 0)),
        "recurrence": Recurrence(
            rrules=[Rule(freq=MONTHLY, bysteps=-1, byday=SA)], dtend=dtend
        ),
    },
]

payload_USSR = {"payload_type": PayloadType.OPPORTUNITY}

contact_RAC = {"title": "RAC", "phone": "+49 30 3009090"}

avatar_RAC = {"pic": "<svg></svg>"}

person_RAC = {"first_name": "John", "middle_name": None, "last_name": "Doe"}

contact_Helter_Skelter = {"title": "Helter Skelter", "phone": "+49 30 3009090"}

organization_RAC_name = "Helter Skelter"
