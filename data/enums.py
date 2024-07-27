from django.db import models


class Languages(models.TextChoices):
    ARABIC = "ar", "العربية"
    ENGLISH = "en", "English"
    GERMAN = "de", "Deutsch"
    FARSI = "fa", "فارسی"
    RUSSIAN = "ru", "Русский"
    TURKISH = "tr", "Türkçe"
    UKRAINIAN = "uk", "Українська"


class LangLevels(models.TextChoices):
    BEGINNER = "beginner", "Beginer"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    FLUENT = "fluent", "Fluent"


class PayloadType(models.TextChoices):
    VOLUNTEER = "volunteer", "Volunteer"
    OPPORTUNITY = "opportunity", "Opportunity"
