from django.db import models


class Languages(models.TextChoices):
    ARABIC = "ar", "Arabic"
    ARMENIAN = "hy", "Armenian"
    BELARUSIAN = "be", "Belarusian"
    CHECHEN = "ce", "Chechen"
    CHINESE = "zh", "Chinese"
    CZECH = "cs", "Czech"
    DARI = "prs", "Dari"
    DUTCH = "nl", "Dutch"
    ENGLISH = "en", "English"
    FRENCH = "fr", "French"
    GEORGIAN = "ka", "Georgian"
    GERMAN = "de", "German"
    GREEK = "el", "Greek"
    HEBREW = "he", "Hebrew"
    HINDI = "hi", "Hindi"
    ITALIAN = "it", "Italian"
    KURMANJI = "kmr", "Kurmanji"
    SORANI = "sdh", "Sorani"
    PASHTO = "ps", "Pashto"
    PERSIAN = "fa", "Farsi"
    POLISH = "pl", "Polish"
    PUNJABI = "pa", "Punjabi"
    ROMANY = "rom", "Roman"
    RUSSIAN = "ru", "Russian"
    SERBIAN = "sr", "Serbian"
    SOMALI = "so", "Somali"
    SPANISH = "es", "Spanish"
    SWEDISH = "sv", "Swedish"
    TURKISH = "tr", "Turkish"
    UKRAINIAN = "uk", "Ukrainian"
    URDU = "ur", "Urdu"
    VIETNAMESE = "vi", "Vietnamese"


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
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    FLUENT = "fluent", "Fluent"
    NATIVE = "native", "Native"


class DEFAULTS:
    OPPORTUNITY_STATUS = "Not started"


class Environment:
    PRODUCTION = "production"
    TEST = "test"
    DEVELOP = "develop"
