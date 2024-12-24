from django.db import models


class Languages(models.TextChoices):
    ARABIC = "ar", "العربية"
    ENGLISH = "en", "English"
    GERMAN = "de", "Deutsch"
    FARSI = "fa", "فارسی"
    RUSSIAN = "ru", "Русский"
    TURKISH = "tr", "Türkçe"
    UKRAINIAN = "uk", "Українська"
    OTHER = "ot", "Other"


class Statuses(models.TextChoices):
    VOLUNTEERS_NEEDED = "Volunteers Needed"
    CHECK_WITH_VC = "Check with the VC"
    URGENT = "Urgent"
    SEARCH_IN_PROGRESS = "Search in Progress"
    NO_VOLUNTEERS_NEEDED = "No Volunteers Needed"
    DONE = "Done"
    INACTIVE = "Inactive"


class BerlinLocations(models.TextChoices):
    CHARLOTTENBURG = "Charlottenburg", "Charlottenburg"
    FRIEDRICHSHAIN = "Friedrichshain", "Friedrichshain"
    HELLERSDORF = "Hellersdorf", "Hellersdorf"
    KOPENICK = "Köpenick", "Köpenick"
    KREUZBERG = "Kreuzberg", "Kreuzberg"
    LICHTENBERG = "Lichtenberg", "Lichtenberg"
    MARZAHN = "Marzahn", "Marzahn"
    MITTE = "Mitte", "Mitte"
    MOABIT = "Moabit", "Moabit"
    NEUKOLLN = "Neukölln", "Neukölln"
    PANKOW = "Pankow", "Pankow"
    PRENZLAUER_BERG = "Prenzlauer Berg", "Prenzlauer Berg"
    REINICKENDORF = "Reinickendorf", "Reinickendorf"
    RUDOW = "Rudow", "Rudow"
    SCHONEBERG = "Schöneberg", "Schöneberg"
    SPANDAU = "Spandau", "Spandau"
    STEGLITZ = "Steglitz", "Steglitz"
    TEGEL = "Tegel", "Tegel"
    TEMPELHOF = "Tempelhof", "Tempelhof"
    TREPTOW = "Treptow", "Treptow"
    WEDDING = "Wedding", "Wedding"
    WEISSENSEE = "Weißensee", "Weißensee"
    WILMERSDORF = "Wilmersdorf", "Wilmersdorf"
    ZEHLENDORF = "Zehlendorf", "Zehlendorf"
    REMOTELY = "Remotely", "Remotely"


class Need4DeedTimeSlots(models.TextChoices):
    MORNING = "08-11", "Morning"
    NOON = "11-14", "Noon"
    AFTERNOON = "14-17", "Afternoon"
    EVENING = "17-20", "Evening"
    WEEKDAYS = "weekdays", "Weekdays"
    WEEKENDS = "weekends", "Weekends"
    GFORM_0810 = "8.00 - 10.00", "08:10"
    GFORM_1012 = "10.00 - 12.00", "10:12"
    GFORM_1214 = "12.00 - 14.00", "12:14"
    GFORM_1416 = "14.00 - 16.00", "14:16"
    GFORM_1618 = "16.00 - 18.00", "16:18"
    GFORM_1820 = "18.00 - 20.00", "18:20"


DAY_CHOICES = [
    (0, "Occasional"),
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]


class OpportunityType(models.TextChoices):
    GENERAL = "volunteering"
    ACCOMPANYING = "accompanying"


class OptionsList:
    LOCATIONS = "locations"
    LANGUAGES = "languages"
    ACTIVITIES = "activities"
    SKILLS = "skills"
    LEADS = "leads"


class LanguageLevel(models.TextChoices):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    FLUENT = "fluent"
    NATIVE = "native"


class DEFAULTS:
    OPPORTUNITY_STATUS = "Not started"


AUTHORIZED_DOMAINS = [
    "lfg-b.de",
    "berliner-stadtmission.de",
    "awo-mitte.de",
    "prisod-wohnen.de",
    "albatrosggmbh.de",
    "gu-oberhafen.de",
    "heroeurope.com",
    "tamaja-gu.de",
    "volkssolidaritaet.de",
    "unionhilfswerk.de",
    "cjd.de",
    "centro-hotels.de",
    "stephanus.org",
    "city54.de",
    "milaa-berlin.de",
    "stk118.de",
    "drk-mueggelspree.de",
    "laf.berlin.de",
    "ejf.de",
    "diakonie-stadtmitte.de",
    "tamaja.de",
    "pgssoziales.de",
    "caritas-berlin.de",
    "need4deed.org",
]
