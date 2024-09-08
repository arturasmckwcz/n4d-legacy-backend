from rest_framework import serializers

from data.enums import OpportunityType
from data.models import (
    Activity,
    Avatar,
    BerlinLocation,
    Contact,
    Language,
    Location,
    Need4DeedDaySchedule,
    Opportunity,
    Organization,
    Person,
    Skill,
    TargetGroup,
    Timeslot,
    VolunteerForm,
)
from data.utils import flatten_dict
from users.serializers import AlfredUserSerializer


class PersonSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    contact = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = [
            "name",
            "first_name",
            "middle_name",
            "last_name",
            "date_of_birth",
            "user",
            "avatar",
            "contact",
            "location",
        ]

    def get_user(self, obj):
        user_details = AlfredUserSerializer(obj.user).data
        if isinstance(user_details, dict):
            del user_details["id"]
        return user_details

    def get_avatar(self, obj):
        avatar = AvatarSerializer(obj.avatar).data
        return avatar

    def get_contact(self, obj):
        contact_details = ContactSerializer(obj.contact).data
        return contact_details

    def get_location(self, obj):
        location_details = LocationSerializer(obj.location).data
        return location_details

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ["pic"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "title",
            "description",
        ]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "title",
            "iso_code",
            "level",
        ]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "title",
            "description",
        ]


class TargetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetGroup
        fields = [
            "title",
            "description",
        ]


class TimeslotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeslot
        fields = [
            "title",
            "start",
            "end",
            "recurrence",
        ]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "title",
            "phone",
            "email",
            "web",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "title",
            "street_address",
            "post_code",
            "city",
            "country",
            "latitude",
            "longitude",
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    persons = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organization
        fields = ["name", "location", "contact", "avatar", "persons"]

    def get_contact(self, obj):
        contact_details = ContactSerializer(obj.contact).data
        return contact_details

    def get_location(self, obj):
        location_details = LocationSerializer(obj.location).data
        return location_details

    def get_avatar(self, obj):
        avatar_details = AvatarSerializer(obj.avatar).data
        return avatar_details

    def get_persons(self, obj):
        persons_details = [
            PersonSerializer(person).data for person in obj.persons.all()
        ]
        return persons_details


class OpportunitySerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField(read_only=True)
    target_groups = serializers.SerializerMethodField(read_only=True)
    locations = serializers.SerializerMethodField(read_only=True)
    timeslots = serializers.SerializerMethodField(read_only=True)
    activities = serializers.SerializerMethodField(read_only=True)
    languages = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)
    opportunity_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "title",
            "target_groups",
            "organization",
            "locations",
            "timeslots",
            "activities",
            "languages",
            "skills",
            "status",
            "vo_information",
            "opportunity_type",
        ]

    def get_organization(self, obj):
        organization_details = OrganizationSerializer(obj.organization).data
        return organization_details

    def get_target_groups(self, obj):
        target_groups_details = [
            TargetGroupSerializer(target_group).data
            for target_group in obj.target_groups.all()
        ]
        return target_groups_details

    def get_locations(self, obj):
        locations_details = [
            LocationSerializer(location).data for location in obj.locations.all()
        ]
        return locations_details

    def get_timeslots(self, obj):
        timeslots_details = [
            TimeslotSerializer(timeslot).data for timeslot in obj.timeslots.all()
        ]
        return timeslots_details

    def get_activities(self, obj):
        activities_details = [
            ActivitySerializer(activity).data for activity in obj.activities.all()
        ]
        return activities_details

    def get_languages(self, obj):
        languages_details = [
            LanguageSerializer(language).data for language in obj.languages.all()
        ]
        translate_language_details = [
            LanguageSerializer(language).data
            for language in obj.translate_languages.all()
        ]
        return languages_details + translate_language_details

    def get_skills(self, obj):
        skills_details = [SkillSerializer(skill).data for skill in obj.skills.all()]
        return skills_details

    def get_opportunity_type(self, obj):
        return (
            OpportunityType.GENERAL
            if len(obj.translate_languages.all()) == 0
            else OpportunityType.ACCOMPANYING
        )

    def to_representation(self, instance):
        primary_keys = self.context.get("primary_keys", None)
        response = super().to_representation(instance)
        return flatten_dict(response, primary_keys)


class VolunteerFormSerialiser(serializers.ModelSerializer):
    schedule = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )
    preffered_berlin_locations = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    languages = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )
    activities = serializers.ListField(child=serializers.CharField(), write_only=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    translate_languages = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )

    class Meta:
        model = VolunteerForm
        exclude = ["notion_id"]
        read_only_fields = ["form_id"]

    def validate_postal_code(self, value):
        if len(str(value)) != 5:
            raise serializers.ValidationError("Postal code should have five digits")
        return value

    def create(self, validated_data):
        schedule_data = validated_data.pop("schedule", [])
        locations_data = validated_data.pop("preffered_berlin_locations", [])
        languages_data = validated_data.pop("languages", [])
        activities_data = validated_data.pop("activities", [])
        skills_data = validated_data.pop("skills", [])
        translate_languages_data = validated_data.pop("translate_languages", [])

        schedule_objects = []
        for day, time_slot in schedule_data:
            day_number = int(day)
            schedule, _ = Need4DeedDaySchedule.objects.get_or_create(
                day=day_number, time_slot=time_slot
            )
            schedule_objects.append(schedule)

        location_objects = []
        for location_name in locations_data:
            location, _ = BerlinLocation.objects.get_or_create(name=location_name)
            location_objects.append(location)

        language_objects = []
        for iso_code, level in languages_data:
            language, _ = Language.objects.get_or_create(
                iso_code=iso_code,
                level=level,
            )
            language_objects.append(language)

        activity_objects = []
        for activity_name in activities_data:
            activity, _ = Activity.objects.get_or_create(title=activity_name)
            activity_objects.append(activity)

        skill_objects = []
        for skill_name in skills_data:
            skill, _ = Skill.objects.get_or_create(title=skill_name)
            skill_objects.append(skill)

        translate_language_objects = []
        for iso_code, level in translate_languages_data:
            language, _ = Language.objects.get_or_create(
                iso_code=iso_code,
                level=level,
            )
            translate_language_objects.append(language)

        volunteer_form = VolunteerForm.objects.create(**validated_data)
        volunteer_form.schedule.set(schedule_objects)
        volunteer_form.preffered_berlin_locations.set(location_objects)
        volunteer_form.languages.set(language_objects)
        volunteer_form.activities.set(activity_objects)
        volunteer_form.skills.set(skill_objects)
        volunteer_form.translate_languages.set(translate_language_objects)

        return volunteer_form
