from django.db import models

from data.enums import LangLevels, Languages, PayloadType
from data.utils import validate_latitude, validate_longitude
from users.models import AlfredUser


class ModelWithTimestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore
        abstract = True


class Timeslot(ModelWithTimestamps):
    title = models.CharField(max_length=32, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    recurrence = models.CharField(max_length=512)


class Location(ModelWithTimestamps):
    title = models.CharField(max_length=32, null=True)

    street_address = models.CharField(max_length=128, null=False)
    post_code = models.CharField(max_length=8, null=False)
    city = models.CharField(max_length=64, null=False)
    country = models.CharField(max_length=64, null=False)

    latitude = models.FloatField(validators=[validate_latitude], null=True)
    longitude = models.FloatField(validators=[validate_longitude], null=True)

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


class TargetGroup(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True)


class Skill(ModelWithTimestamps):
    title = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128, null=True)


class Language(ModelWithTimestamps):
    iso_code = models.CharField(choices=Languages.choices, unique=True, max_length=2)
    level = models.CharField(
        choices=LangLevels.choices, max_length=16, default=LangLevels.FLUENT
    )


class Contact(ModelWithTimestamps):
    title = models.CharField(max_length=32, null=True)

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
        return self.name


class Organization(ModelWithTimestamps):
    name = models.CharField(max_length=128, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    persons = models.ManyToManyField("data.Person", blank=True)

    def __str__(self):
        return f"{self.name}"


class Payload(ModelWithTimestamps):
    payload_type = models.CharField(choices=PayloadType.choices, max_length=16)
    timeslots = models.ManyToManyField(Timeslot)
    activities = models.ManyToManyField(Activity)
    locations = models.ManyToManyField(Location)
    languages = models.ManyToManyField(Language)
    skills = models.ManyToManyField(Skill)


class Opportunity(ModelWithTimestamps):
    title = models.CharField(max_length=128, default="Good Samaritan")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    volunteers_number = models.IntegerField(default=1)
    target_groups = models.ManyToManyField(TargetGroup)
    payload = models.OneToOneField(Payload, on_delete=models.CASCADE)
