from datetime import datetime, timezone

from recurrence import MO, MONTHLY, SA, WEEKLY, Recurrence, Rule

utc_tz = timezone.utc
dtend = datetime(2025, 12, 31, 0, 0, 0, tzinfo=utc_tz)

location_Helter_Skelter = {
    "title": "Gotham RAC",
    "street_address": "Outskirt Strasse 420",
    "post_code": "99007",
    "city": "Gotham",
    "country": "USA",
}
locations = [
    {
        "title": "USSR",
        "street_address": "Hölle Platz 1",
        "post_code": "00666",
        "city": "Moscow",
        "country": "USSR",
    },
    {
        "title": "Inner Mongolia",
        "latitude": 47.80780396727952,
        "longitude": 106.95299192104217,
    },
]

languages = [
    {
        "title": "German",
        "iso_code": "de",
        "level": "fluent",
    },
    {
        "title": "English",
        "iso_code": "en",
        "level": "fluent",
    },
    {
        "title": "French",
        "iso_code": "fr",
        "level": "fluent",
    },
    {
        "title": "Arabic",
        "iso_code": "ar",
        "level": "fluent",
    },
    {
        "title": "Farsi",
        "iso_code": "fa",
        "level": "fluent",
    },
    {
        "title": "Ukrainian",
        "iso_code": "uk",
        "level": "fluent",
    },
    {
        "title": "Russian",
        "iso_code": "ru",
        "level": "fluent",
    },
    {
        "title": "Italian",
        "iso_code": "it",
        "level": "fluent",
    },
    {
        "title": "Spanish",
        "iso_code": "es",
        "level": "fluent",
    },
]

activities = [
    {"title": "Daycare"},
    {"title": "Translation"},
    {"title": "Sports"},
]

target_groups = [
    {"title": "Kids"},
    {"title": "Women"},
    {"title": "Men"},
]

skills = [
    {"title": "Music"},
    {"title": "Football"},
    {"title": "Teaching"},
]

timeslots = [
    {
        "title": "Monday Morning",
        "start": datetime(2024, 10, 7, 8, 8, 0, 0, tzinfo=utc_tz),
        "end": datetime(2024, 10, 7, 8, 11, 0, 0, tzinfo=utc_tz),
        "recurrence": str(Recurrence(rrules=[Rule(freq=WEEKLY, wkst=MO)], dtend=dtend)),
    },
    {
        "title": "Last Saturday Noon",
        "start": datetime(2024, 7, 27, 12, 11, 0, 0, tzinfo=utc_tz),
        "end": datetime(2024, 7, 27, 14, 14, 0, 0, tzinfo=utc_tz),
        "recurrence": str(
            Recurrence(rrules=[Rule(freq=MONTHLY, bysteps=-1, byday=SA)], dtend=dtend)
        ),
    },
]

contact_RAC = {"title": "RAC", "phone": "+49 30 3009090"}

avatar_RAC = {"pic": "<svg></svg>"}

person_RAC = {"first_name": "John", "middle_name": None, "last_name": "Doe"}

contact_Helter_Skelter = {"title": "Helter Skelter", "phone": "+49 30 3009090"}

organization_RAC_name = "Helter Skelter"

lichtenberg_opportunity_flattered = {
    "id": 1,
    "title": "Support with homework in Lichtenberg",
    "status": "Volunteers Needed",
    "target_groups": ["Kids", "Teenagers"],
    "berlin_locations": ["Lichtenberg"],
    "schedule_str": None,
    "activities": ["Tutoring"],
    "languages": [],
    "skills": [],
    "vo_information": "The kids speak German, we don’t know anything about their ages or grades. They would need help with various subjects.",
}
