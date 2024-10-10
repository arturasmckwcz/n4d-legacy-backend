import uuid

from django.db import models

from data.enums import (
    BerlinLocations,
    LanguageLevel,
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
    title = models.CharField(max_length=128, db_index=True)
    iso_code = models.CharField(max_length=3, db_index=True)

    def __str__(self):
        return f"{self.iso_code} | {self.title}"


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


class LanguageM2M(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class OpportunityLanguageM2M(LanguageM2M):
    opportunity = models.ForeignKey("data.opportunity", on_delete=models.CASCADE)


class Opportunity(ModelWithTimestamps):
    title = models.CharField(max_length=128, default="Good Samaritan")
    opportunity_type = models.CharField(
        choices=OpportunityType.choices, default=OpportunityType.GENERAL
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    volunteers_number = models.IntegerField(default=1)
    datetime_str = models.CharField(max_length=128, null=True, blank=True)
    timeslots = models.ManyToManyField(Timeslot, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    berlin_locations = models.ManyToManyField(BerlinLocation)
    languages = models.ManyToManyField(
        Language,
        through=OpportunityLanguageM2M,
        blank=True,
    )
    skills = models.ManyToManyField(Skill, blank=True)
    notion_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, blank=True, null=True
    )
    status = models.CharField(max_length=128, db_index=True)
    vo_information = models.TextField(blank=True, null=True)
    last_edited_time_notion = models.DateTimeField(null=True)
    schedule_str = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.title


class Need4DeedDaySchedule(models.Model):
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
    day = models.IntegerField(choices=DAY_CHOICES)
    time_slot = models.CharField(
        max_length=20, choices=Need4DeedTimeSlots.choices, default=None
    )

    class Meta:
        unique_together = ["day", "time_slot"]

    def __str__(self):
        return f"{self.DAY_CHOICES[self.day][1]} - {self.time_slot}"


class VolunteerLanguageM2M(LanguageM2M):
    volunteerform = models.ForeignKey("data.volunteerform", on_delete=models.CASCADE)
    level = models.CharField(choices=LanguageLevel.choices, null=True)


class VolunteerForm(ModelWithTimestamps):
    form_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=True, unique=True)
    email = models.EmailField(null=False, unique=True)
    schedule = models.ManyToManyField(Need4DeedDaySchedule)
    postal_code = models.IntegerField()
    preferred_berlin_locations = models.ManyToManyField(BerlinLocation)
    languages = models.ManyToManyField(Language, through=VolunteerLanguageM2M)
    if_good_conduct_certificate = models.BooleanField(null=True)
    if_measles_vaccination = models.BooleanField(null=True)
    activities = models.ManyToManyField(Activity)
    lead_from = models.CharField(max_length=1024, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    comments = models.CharField(max_length=1024, null=True, blank=True)
    notion_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, blank=True, null=True
    )
    origin_opportunity_id = models.ForeignKey(
        Opportunity, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_edited_time_notion = models.DateTimeField(null=True)
