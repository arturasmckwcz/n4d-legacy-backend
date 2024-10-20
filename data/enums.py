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
    MORNING = "morning", "Morning"
    NOON = "noon", "Noon"
    AFTERNOON = "afternoon", "Afternoon"
    EVENING = "evening", "Evening"
    WEEKDAYS = "weekdays", "Weekdays"
    WEEKENDS = "weekends", "Weekends"


class OpportunityType(models.TextChoices):
    GENERAL = "Volunteering"
    ACCOMPANYING = "Accompanying"


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
