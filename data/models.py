import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction

from data.enums import (
    DAY_CHOICES,
    DEFAULTS,
    BerlinLocations,
    LanguageLevel,
    Languages,
    Need4DeedTimeSlots,
    OpportunityType,
)
from data.utils import validate_latitude, validate_longitude
from users.models import AlfredUser


class ModelWithTimestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Timeslot(models.Model):
    title = models.CharField(max_length=128, unique=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    recurrence = models.CharField(max_length=512, null=True)

    def __str__(self):
        return self.title


class Location(ModelWithTimestamps):
    title = models.CharField(max_length=128, unique=True, default="Location title")
    street_address = models.CharField(max_length=128, blank=True)
    post_code = models.CharField(max_length=8, blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128, blank=True)
    latitude = models.FloatField(validators=[validate_latitude], blank=True, null=True)
    longitude = models.FloatField(
        validators=[validate_longitude], blank=True, null=True
    )

    def __str__(self):
        title = self.title
        return (
            f"{title}"
            if title
            else f"{self.street_address}\n{self.post_code} {self.city}\n{self.country}"
        )


class Activity(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class Skill(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class FormLeadFrom(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class Language(models.Model):
    iso_code = models.CharField(max_length=3, choices=Languages.choices, unique=True)
    title = models.CharField(max_length=25)

    def get_title(self, language_code="de"):
        translation = self.translations.filter(language__iso_code=language_code).first()  # pyright: ignore[reportAttributeAccessIssue]
        return translation.title if translation else self.title

    def __str__(self):
        return f"{self.iso_code} {self.title}"


class LanguageTranslation(models.Model):
    language_obj = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)

    class Meta:
        unique_together = ("language_obj", "language")


class Contact(ModelWithTimestamps):
    title = models.CharField(max_length=128, unique=True)
    phone = models.CharField(max_length=64, null=True)
    email = models.EmailField(null=True)
    web = models.URLField(null=True)

    def __str__(self):
        title = self.title
        return (
            f"'{title}'"
            if title
            else f"Phone: '{self.phone}'\nEmail: '{self.email}'\nWeb: '{self.web}'"
        )


class BerlinLocation(models.Model):
    name = models.CharField(
        max_length=128, unique=True, choices=BerlinLocations.choices
    )

    def __str__(self):
        return self.name


class Avatar(ModelWithTimestamps):
    pic = models.CharField(max_length=10 * 1024)


class Person(ModelWithTimestamps):
    user = models.OneToOneField(AlfredUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    middle_name = models.CharField(max_length=128, null=True)
    date_of_birth = models.DateTimeField(null=True)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    organizations = models.ManyToManyField("data.Organization", blank=True)

    @property
    def name(self):
        middle_name = self.middle_name
        middle_name = f" {middle_name}" if middle_name else ""
        return f"{self.first_name}{middle_name} {self.last_name}"

    def __str__(self):
        return f"{self.name}"


class Organization(ModelWithTimestamps):
    name = models.CharField(max_length=512, null=False, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    persons = models.ManyToManyField("data.Person", blank=True)

    def __str__(self):
        return f"{self.name}"


class Need4DeedDaySchedule(models.Model):
    day = models.IntegerField(choices=DAY_CHOICES)
    time_slot = models.CharField(
        max_length=20, choices=Need4DeedTimeSlots.choices, default=None
    )

    class Meta:
        unique_together = ["day", "time_slot"]

    def __str__(self):
        return f"{DAY_CHOICES[self.day][1]} - {self.time_slot}"


"""
SELECT o.id, o.rac_email, l.title, t.title FROM data_opportunity o JOIN data_opportunitytranslation t ON t.opportunity_id=o.id JOIN data_language l ON l.id=t.language_id;
"""


class Opportunity(ModelWithTimestamps):
    rac_email = models.EmailField(null=True, blank=True)
    rac_full_name = models.CharField(max_length=128, null=True, blank=True)
    rac_address = models.CharField(max_length=128, null=True, blank=True)
    rac_plz = models.IntegerField(null=True, blank=True)
    rac_phone = models.CharField(max_length=64, null=True, blank=True)
    opportunity_type = models.CharField(
        choices=OpportunityType.choices, default=OpportunityType.GENERAL
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    volunteers_number = models.IntegerField(default=1)
    datetime_str = models.CharField(max_length=128, null=True, blank=True)
    timeslots = models.ManyToManyField(Need4DeedDaySchedule, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    berlin_locations = models.ManyToManyField(BerlinLocation)
    accomp_address = models.CharField(max_length=128, null=True, blank=True)
    accomp_datetime = models.DateTimeField(null=True, blank=True)
    accomp_name = models.CharField(max_length=128, null=True, blank=True)
    accomp_phone = models.CharField(max_length=64, null=True, blank=True)
    accomp_postcode = models.CharField(null=True, blank=True)
    accomp_translation = models.CharField(max_length=256, null=True, blank=True)
    languages = models.ManyToManyField(Language)
    skills = models.ManyToManyField(Skill, blank=True)
    notion_id = models.UUIDField(
        default=None, editable=False, unique=True, blank=True, null=True
    )
    status = models.CharField(
        max_length=128, default=DEFAULTS.OPPORTUNITY_STATUS, db_index=True
    )
    last_edited_time_notion = models.DateTimeField(null=True, blank=True)
    schedule_str = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        german = self.translations.filter(language__iso_code="de").first()  # pyright: ignore[reportAttributeAccessIssue]
        return f"{german.title if german else 'No title'} | {self.rac_email}"

    def get_title(self, language_code="de"):
        translation = self.translations.filter(language__iso_code=language_code).first()  # pyright: ignore[reportAttributeAccessIssue]
        return translation.title if translation else None

    def get_vo_information(self, language_code="de"):
        translation = self.translations.filter(language__iso_code=language_code).first()  # pyright: ignore[reportAttributeAccessIssue]
        return translation.vo_information if translation else None

    def get_accomp_information(self, language_code="de"):
        translation = self.translations.filter(language__iso_code=language_code).first()  # pyright: ignore[reportAttributeAccessIssue]
        return translation.accomp_information if translation else None

    @classmethod
    def create_with_translation(
        cls,
        german_title,
        german_vo_information=None,
        german_accomp_information=None,
        **opportunity_fields,
    ):
        """
        Creates an Opportunity instance together with its mandatory German translation.
        This method ensures that every Opportunity is created with a German title and description,
        maintaining data integrity by using a database transaction.

        Args:
            german_title (str): The German title of the opportunity (required)
            german_vo_information (str): The German description/information (optional)
            german_accomp_information (str): The German description/information (optional)
            **opportunity_fields: Additional fields for the Opportunity model (e.g., rac_email, status)

        Returns:
            Opportunity: The created Opportunity instance with its German translation

        Example:
            opportunity = Opportunity.create_with_translation(
                german_title="Neue Gelegenheit",
                german_vo_information="Beschreibung",
                rac_email="example@email.com"
            )

        Raises:
            IntegrityError: If the German language doesn't exist in the database
            ValidationError: If required fields are missing
        """
        with transaction.atomic():
            opportunity = cls.objects.create(**opportunity_fields)
            OpportunityTranslation.objects.create(
                opportunity=opportunity,
                language=Language.objects.get(iso_code="de"),
                title=german_title,
                vo_information=german_vo_information,
                accomp_information=german_accomp_information,
            )
            return opportunity


class OpportunityTranslation(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    vo_information = models.TextField(blank=True, null=True)
    accomp_information = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("opportunity", "language")

    def save(self, *args, **kwargs):
        if (
            self.language.iso_code != "de"
            and not self.opportunity.translations.filter(  # pyright: ignore[reportAttributeAccessIssue]
                language__iso_code="de"
            ).exists()
        ):
            raise ValidationError("German translation must be created first")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.opportunity.pk} | {self.language.iso_code}"


class VolunteerForm(ModelWithTimestamps):
    form_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=True, unique=True)
    email = models.EmailField(null=False, unique=True)
    schedule = models.ManyToManyField(Need4DeedDaySchedule)
    postal_code = models.IntegerField()
    preferred_berlin_locations = models.ManyToManyField(BerlinLocation)
    good_conduct_certificate = models.CharField(max_length=64, null=True)
    if_measles_vaccination = models.BooleanField(null=True)
    activities = models.ManyToManyField(Activity)
    lead_from = models.CharField(max_length=1024, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    comments = models.CharField(max_length=1024, null=True, blank=True)
    comments_workflow = models.CharField(max_length=1024, null=True, blank=True)
    notion_id = models.UUIDField(editable=False, unique=True, blank=True, null=True)
    origin_opportunity = models.ForeignKey(
        Opportunity, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_edited_time_notion = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.full_name} | email: {self.email}"


class VolunteerLanguage(models.Model):
    volunteer_form = models.ForeignKey(
        VolunteerForm, on_delete=models.CASCADE, related_name="languages"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=12, choices=LanguageLevel.choices)

    class Meta:
        unique_together = ["volunteer_form", "language"]

    def __str__(self):
        return f"{self.language.title} {self.level}"
