from django.db import models

from data.enums import LangLevels, Languages, Statuses
from data.utils import validate_latitude, validate_longitude
from users.models import AlfredUser


class ModelWithTimestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore
        abstract = True


class Timeslot(ModelWithTimestamps):
    title = models.CharField(max_length=64, unique=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    recurrence = models.CharField(max_length=512, null=True)

    def __str__(self):
        return self.title


class Location(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True, default="Location title")
    street_address = models.CharField(max_length=128, blank=True)
    post_code = models.CharField(max_length=8, blank=True)
    city = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)
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


class Activity(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class TargetGroup(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class Skill(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.title


class Language(ModelWithTimestamps):
    iso_code = models.CharField(choices=Languages.choices, max_length=2)
    level = models.CharField(
        choices=LangLevels.choices, max_length=16, default=LangLevels.FLUENT
    )

    def __str__(self):
        return self.iso_code


class Contact(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
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


class Opportunity(ModelWithTimestamps):
    title = models.CharField(max_length=128, default="Good Samaritan")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    volunteers_number = models.IntegerField(default=1)
    target_groups = models.ManyToManyField(TargetGroup, blank=True)
    timeslots = models.ManyToManyField(Timeslot, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    locations = models.ManyToManyField(Location)
    languages = models.ManyToManyField(Language)
    skills = models.ManyToManyField(Skill, blank=True)
    notion_id = models.CharField(max_length=16, unique=True)
    status = models.CharField(choices=Statuses.choices, max_length=48)
    vo_information = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
