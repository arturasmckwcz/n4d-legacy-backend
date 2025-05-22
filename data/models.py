import uuid
from typing import Literal

import structlog
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from alfred.settings import ENV
from alfred.translation_handler import translate
from data.enums import (
    DAY_CHOICES,
    DEFAULTS,
    BerlinLocations,
    Environment,
    EventN4DType,
    LanguageLevel,
    Languages,
    Need4DeedTimeSlots,
    OpportunityType,
)
from data.utils import validate_latitude, validate_longitude
from users.models import AlfredUser

logger = structlog.get_logger(__name__)


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


def get_field_translation(obj, language_iso_code, field="title"):
    obj_field = getattr(obj, field) if hasattr(obj, field) else None

    try:
        content_type = ContentType.objects.get_for_model(obj)
    except ContentType.DoesNotExist:
        logger.error(f"Model {obj} happens to be missing in ContentType")
        return obj_field

    translation = TitleTranslation.objects.filter(
        content_type=content_type,
        field=field,
        object_id=obj.pk,
        language__iso_code=language_iso_code,
    ).first()
    return translation.translation if translation else obj_field


class Activity(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    def get_title(self, language_code="de"):
        return get_field_translation(self, language_code)

    @property
    def translated_title_de(self):
        return get_field_translation(self, "de")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Activities"


class Skill(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    @property
    def translated_title_de(self):
        return get_field_translation(self, "de")

    def get_title(self, language_code="de"):
        return get_field_translation(self, language_code)

    def __str__(self):
        return self.title


class FormLeadFrom(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, null=True)

    def get_title(self, language_code="de"):
        return get_field_translation(self, language_code)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Form leads from"


class Language(models.Model):
    iso_code = models.CharField(max_length=3, choices=Languages.choices, unique=True)
    title = models.CharField(max_length=25)

    def get_title(self, language_code="de"):
        translation = self.translations.filter(language__iso_code=language_code).first()  # pyright: ignore[reportAttributeAccessIssue]
        return translation.title if translation else self.title

    @classmethod
    def get_language_obj(cls, iso_code: str):
        return cls.objects.filter(iso_code=iso_code).first()

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


class TitleTranslation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    field = models.CharField(max_length=64, null=True, blank=True, default="title")
    translation = models.CharField(max_length=1024)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="translations"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("language", "content_type", "object_id")

    def __str__(self):
        title = (
            self.translation
            if len(self.translation) <= 48
            else f"{self.translation[:48]} ..."
        )
        return f"{self.content_object} [{self.language.iso_code}]: {title}"


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


ObjectType = Literal["Opportunity", "EventN4D"]
ObjectTranslationType = Literal["OpportunityTranslation", "EventTranslation"]


def get_translated_object_field(
    obj: ObjectType,
    language_code: str,
    field: str,
    translation_model: ObjectTranslationType,
    translation_object_field: str,
    max_length: int | None = None,
    is_list: bool = False,
) -> str | None:
    """
    Helper: Gets the translated field of an object.
    Args:
        obj (ObjectType): The object to translate.
        language_code (str): The language code to translate to.
        field (str): The field to translate.
        translation_model (ObjectTranslationType): The translation model.
        translation_object_field (str): The translation object field.
        max_length (int | None): The maximum length of the translated text.
        is_list (bool): Whether the field is a list or not.
    Returns:
        str | None: The translated text or None if not found.
    Raises:
        ValueError: If the language code is unknown.
    """

    def _create_or_update_translation_obj(
        obj: ObjectType,
        language: Language,
        field: str,
        translated_text: str,
        max_length: int | None,
        translation_model: ObjectTranslationType,
        translation_object_field: str,
        existing_translation: ObjectTranslationType | None = None,
    ) -> ObjectTranslationType:
        """Helper: Creates or updates a translation object."""

        if existing_translation:
            setattr(existing_translation, field, translated_text[:max_length])
            existing_translation.save()
            return existing_translation
        else:
            translation_kwargs = {
                field: translated_text[:max_length],
                translation_object_field: obj,
                "language": language,
            }
            new_translation = translation_model(**translation_kwargs)
            new_translation.save()
            return new_translation

    def _translate_list(original_text: list) -> list[str]:
        """
        Helper: Translates a list of strings.
        """
        delimiter = "<|>"

        text_for_translation = (
            original_text.join(delimiter)
            if isinstance(original_text, list)
            else original_text
        )

        translated_text = translate(
            text=text_for_translation,
            source_language_code=getattr(obj.original_language, "iso_code"),
            target_language_code=language_code,
            dry_run=ENV != Environment.PRODUCTION,
        )
        return (
            translated_text.split(delimiter)
            if isinstance(original_text, list)
            else translated_text
        )

    language = Language.get_language_obj(language_code)

    if not language:
        raise ValueError("Unknown language")

    existing_translation = obj.get_translation(language)

    if existing_translation and getattr(existing_translation, field):
        return getattr(existing_translation, field)

    original_translation = obj.get_translation(obj.original_language)

    if original_translation:
        original_text = getattr(original_translation, field)
        if not original_text:
            return None

        translated_text = (
            translate(
                text=original_text,
                source_language_code=getattr(obj.original_language, "iso_code"),
                target_language_code=language_code,
                dry_run=ENV != Environment.PRODUCTION,
            )
            if not is_list
            else _translate_list(original_text)
        )

        if translated_text:
            final_translation = _create_or_update_translation_obj(
                obj=obj,
                language=language,
                field=field,
                translated_text=translated_text,
                existing_translation=existing_translation,
                max_length=max_length,
                translation_model=translation_model,
                translation_object_field=translation_object_field,
            )
            return getattr(final_translation, field)
        else:
            logger.error('Translation of "{text}" to "{language_code}" returned null')
            return original_text

    return None


class Opportunity(ModelWithTimestamps):
    original_language = models.ForeignKey(
        Language,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="original_language",
    )
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

    def get_title(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="title",
            max_length=256,
            translation_model=OpportunityTranslation,
            translation_object_field="opportunity",
        )

    def get_vo_information(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="vo_information",
            translation_model=OpportunityTranslation,
            translation_object_field="opportunity",
        )

    def get_accomp_information(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="accomp_information",
            translation_model=OpportunityTranslation,
            translation_object_field="opportunity",
        )

    def get_translation(self, language: Language):
        return self.translations.filter(language=language).first()

    @classmethod
    def create_with_translation(
        cls,
        title,
        original_language_iso="de",
        vo_information=None,
        accomp_information=None,
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
            original_language = Language.objects.filter(
                iso_code=original_language_iso
            ).first()
            opportunity.original_language = original_language
            opportunity.save()
            OpportunityTranslation.objects.create(
                opportunity=opportunity,
                language=original_language,
                title=title,
                vo_information=vo_information,
                accomp_information=accomp_information,
            )
            return opportunity

    class Meta:
        verbose_name_plural = "Opportunities"


class OpportunityTranslation(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, blank=True, null=True)
    vo_information = models.TextField(blank=True, null=True)
    accomp_information = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("opportunity", "language")

    def save(self, *args, **kwargs):
        if not self.opportunity.original_language:
            self.opportunity.original_language = self.language

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.opportunity.pk} | {self.language.iso_code}"


class AuthEmailDomain(models.Model):
    domain = models.CharField(max_length=128)

    @classmethod
    def is_domain_authorized(cls, domain: str):
        return cls.objects.filter(domain=domain).exists()

    def __str__(self):
        return f"{self.domain}"


class Testimonial(models.Model):
    original_language = models.ForeignKey(
        Language,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="testimonial_original_language",
    )
    name = models.CharField(max_length=128, null=True, blank=True)
    volunteer_form = models.ForeignKey(
        "VolunteerForm", on_delete=models.SET_NULL, null=True, blank=True
    )
    pic = models.TextField(null=True, blank=True)
    activities = models.ManyToManyField(Activity)
    is_active = models.BooleanField(default=True)

    def get_translated_text(self, iso_code):
        return get_field_translation(self, iso_code, field="translated_text")

    def __str__(self):
        name, *_ = (
            self.volunteer_form.full_name.split(" ")
            if self.volunteer_form
            else (self.name,)
        )
        active = "👍🏼"
        inactive = "👎"
        return (
            f"Testimonial {self.id} of {name} {active if self.is_active else inactive}"
        )


class VolunteerForm(ModelWithTimestamps):
    form_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=True)
    email = models.EmailField(null=False)
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

    def check_email_and_phone(self):
        """
        Check if the email and phone number are already used by another volunteer form.
        """

        email = (
            self.email
            if VolunteerForm.objects.filter(email=self.email)
            .exclude(form_id=self.form_id)
            .exists()
            else None
        )
        phone = (
            self.phone
            if VolunteerForm.objects.filter(phone=self.phone)
            .exclude(form_id=self.form_id)
            .exists()
            else None
        )

        return (email, phone)

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


class EventN4D(models.Model):
    """
    Django model representing an event based on the EventN4D TypeScript interface.
    """

    original_language = models.ForeignKey(
        Language,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="event_original_language",
    )
    active = models.BooleanField(default=False)
    host_name = models.CharField(max_length=256, blank=True, null=True)
    date = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(
        max_length=20,
        choices=EventN4DType.choices,
        default=EventN4DType.PARTY,
    )
    pic = models.CharField(max_length=256, blank=True, null=True)
    address = models.CharField(max_length=256)
    location_link = models.URLField(blank=True, null=True)
    linkRSVP = models.URLField()
    followup_link = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Event N4D"
        verbose_name_plural = "Events N4D"

        constraints = [
            models.UniqueConstraint(
                fields=["active"],
                condition=models.Q(active=True),
                name="one_active_event",
            )
        ]

    def get_translation(self, language: Language):
        return self.event_translations.filter(language=language).first()

    def __str__(self):
        return self.get_title("en") or f"Event {self.pk} | {self.date}"

    def get_title(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="title",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_subtitle(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="subtitle",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_menu_title(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="menu_title",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_time_str(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="time_str",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_location_comment(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="location_comment",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_description(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="description",
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_short_description(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="short_description",
            max_length=512,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_followup_text(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="followup_text",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_additional_title(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="additional_title",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )

    def get_additional_info(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="additional_info",
            translation_model=EventTranslation,
            translation_object_field="event",
            is_list=True,
        )

    def get_outro(self, iso_code="de"):
        return get_translated_object_field(
            self,
            language_code=iso_code,
            field="outro",
            max_length=256,
            translation_model=EventTranslation,
            translation_object_field="event",
        )


class EventTranslation(models.Model):
    event = models.ForeignKey(
        EventN4D, on_delete=models.CASCADE, related_name="event_translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    title = models.CharField(max_length=256, blank=True, null=True)
    subtitle = models.CharField(max_length=256, blank=True, null=True)
    menu_title = models.CharField(max_length=256, blank=True, null=True)
    time_str = models.CharField(max_length=256, blank=True, null=True)
    location_comment = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField()
    short_description = models.CharField(max_length=512)
    followup_text = models.CharField(max_length=256, blank=True, null=True)
    additional_title = models.CharField(max_length=256, blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)
    outro = models.TextField(max_length=256, blank=True, null=True)

    class Meta:
        unique_together = ("event", "language")

    def save(self, *args, **kwargs):
        if not self.event.original_language:
            self.event.original_language = self.language

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event.pk} | {self.language.iso_code}"


# GenericForeignKey doesn't provide the option for chained deletion
# so here's listening to post_delete signal
@receiver(post_delete, sender=Activity)
@receiver(post_delete, sender=Skill)
@receiver(post_delete, sender=FormLeadFrom)
@receiver(post_delete, sender=Testimonial)
def delete_title_translations(sender, instance, **kwargs):
    TitleTranslation.objects.filter(
        content_type=ContentType.objects.get_for_model(sender), object_id=instance.pk
    ).delete()
