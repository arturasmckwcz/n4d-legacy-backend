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


class LangLevels(models.TextChoices):
    BEGINNER = "beginner", "Beginer"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    FLUENT = "fluent", "Fluent"


class PayloadType(models.TextChoices):
    VOLUNTEER = "volunteer", "Volunteer"
    OPPORTUNITY = "opportunity", "Opportunity"
