from rest_framework import serializers

from data.models import (
    Activity,
    Avatar,
    Contact,
    Language,
    Location,
    Opportunity,
    Organization,
    Payload,
    Person,
    Skill,
    TargetGroup,
    Timeslot,
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


class PayloadSerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField(read_only=True)
    timeslots = serializers.SerializerMethodField(read_only=True)
    activities = serializers.SerializerMethodField(read_only=True)
    languages = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payload
        fields = [
            "locations",
            "payload_type",
            "timeslots",
            "activities",
            "languages",
            "skills",
        ]

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
        return languages_details

    def get_skills(self, obj):
        skills_details = [SkillSerializer(skill).data for skill in obj.skills.all()]
        return skills_details


class OpportunitySerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField(read_only=True)
    target_groups = serializers.SerializerMethodField(read_only=True)
    payload = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "title",
            "volunteers_number",
            "target_groups",
            "organization",
            "payload",
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

    def get_payload(self, obj):
        payload_details = PayloadSerializer(obj.payload).data
        return payload_details

    def to_representation(self, instance):
        primary_keys = self.context.get("primary_keys", None)
        response = super().to_representation(instance)
        return flatten_dict(response, primary_keys)
