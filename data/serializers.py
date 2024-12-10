import structlog
from rest_framework import serializers

from data.enums import AUTHORIZED_DOMAINS, LanguageLevel
from data.models import (
    Activity,
    Avatar,
    BerlinLocation,
    Contact,
    FormLeadFrom,
    Language,
    Location,
    Need4DeedDaySchedule,
    Opportunity,
    Organization,
    Person,
    Skill,
    Timeslot,
    VolunteerForm,
    VolunteerLanguageM2M,
)
from data.utils import flatten_dict
from users.serializers import AlfredUserSerializer

logger = structlog.get_logger(__name__)


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
            "id",
            "title",
            "iso_code",
        ]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "title",
            "description",
        ]


class FormLeadFromSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLeadFrom
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


class BerlinLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BerlinLocation
        fields = [
            "name",
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
    berlin_locations = serializers.SerializerMethodField(read_only=True)
    activities = serializers.SerializerMethodField(read_only=True)
    languages = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "opportunity_type",
            "berlin_locations",
            "schedule_str",
            "datetime_str",
            "activities",
            "languages",
            "skills",
            "status",
            "vo_information",
            "opportunity_type",
        ]

    def get_berlin_locations(self, obj):
        berlin_locations_details = [
            BerlinLocationSerializer(berlin_location).data
            for berlin_location in obj.berlin_locations.all()
        ]
        return berlin_locations_details

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

    def to_representation(self, instance):
        primary_keys = self.context.get("primary_keys", None)
        response = super().to_representation(instance)
        return flatten_dict(response, primary_keys)


class OpportunityCreateSerializer(serializers.ModelSerializer):
    berlin_locations = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    languages = serializers.ListField(child=serializers.CharField(), write_only=True)
    activities = serializers.ListField(child=serializers.CharField(), write_only=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    timeslots = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )

    def validate_rac_email(self, value):
        _, domain = value.split("@")
        if domain.lower() not in AUTHORIZED_DOMAINS:
            raise serializers.ValidationError("Attempt of unauthorized access.")
        return value

    def validate_rac_postal_code(
        self, value
    ):  # 01001-95999 range for Deutschland and 10115-14199 for Berlin
        if value < 1001 or value > 95999:
            raise serializers.ValidationError(
                "Postal code should be between 01001 and 95999"
            )
        return value

    def create(self, validated_data):
        berlin_locations_data = validated_data.pop("berlin_locations", [])
        berlin_locations = []
        for location_name in berlin_locations_data:
            location, _ = BerlinLocation.objects.get_or_create(name=location_name)
            berlin_locations.append(location)

        activities_data = validated_data.pop("activities", [])
        activities = []
        for activity_name in activities_data:
            activity, _ = Activity.objects.get_or_create(title=activity_name)
            activities.append(activity)

        skills_data = validated_data.pop("skills", [])
        skills = []
        for skill_name in skills_data:
            skill, _ = Skill.objects.get_or_create(title=skill_name)
            skills.append(skill)

        languages_data = validated_data.pop("languages", [])
        languages = []
        for language_name in languages_data:
            language = Language.objects.get(title=language_name)
            languages.append(language)

        timeslots_data = validated_data.pop("timeslots", [])
        timeslots = []
        for day, time_slot in timeslots_data:
            logger.debug(f"{day=}, {time_slot=}")
            day_number = int(day)
            timeslot_object, _ = Need4DeedDaySchedule.objects.get_or_create(
                day=day_number, time_slot=time_slot
            )
            timeslots.append(timeslot_object)

        oppotunity_object = Opportunity.objects.create(**validated_data)
        oppotunity_object.berlin_locations.set(berlin_locations)
        oppotunity_object.activities.set(activities)
        oppotunity_object.skills.set(skills)
        oppotunity_object.languages.set(languages)
        oppotunity_object.timeslots.set(timeslots)
        return oppotunity_object

    class Meta:
        model = Opportunity
        fields = "__all__"


class VolunteerFormSerializer(serializers.ModelSerializer):
    schedule = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )
    preferred_berlin_locations = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    native_languages = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
    )
    fluent_languages = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )
    intermediate_languages = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )
    activities = serializers.ListField(child=serializers.CharField(), write_only=True)
    skills = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = VolunteerForm
        exclude = ["notion_id", "last_edited_time_notion"]
        read_only_fields = ["form_id"]

    def validate_postal_code(
        self, value
    ):  # 01001-95999 range for Deutschland and 10115-14199 for Berlin
        if value < 1001 or value > 95999:
            raise serializers.ValidationError(
                "Postal code should be between 01001 and 95999"
            )
        return value

    def get_language_title(self, title: str) -> str:
        if title == "Farsi":
            return "Persian"
        return title

    def create(self, validated_data):
        schedule_data = validated_data.pop("schedule", [])
        locations_data = validated_data.pop("preferred_berlin_locations", [])
        activities_data = validated_data.pop("activities", [])
        skills_data = validated_data.pop("skills", [])
        native_languages_data = validated_data.pop("native_languages", [])
        fluent_languages_data = validated_data.pop("fluent_languages", [])
        intermediate_languages_data = validated_data.pop("intermediate_languages", [])

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

        native_language_objects = []
        for title in native_languages_data:
            try:
                language = Language.objects.get(
                    title=self.get_language_title(title),
                )
                native_language_objects.append(language)
            except Exception as e:
                logger.error(
                    f"Error {e} occurred while parsing native language {title}"
                )

        fluent_language_objects = []
        for title in fluent_languages_data:
            try:
                language = Language.objects.get(
                    title=self.get_language_title(title),
                )
                fluent_language_objects.append(language)
            except Exception as e:
                logger.error(
                    f"Error {e} occurred while parsing fluent language {title}"
                )

        intermediate_language_objects = []
        for title in intermediate_languages_data:
            try:
                language = Language.objects.get(
                    title=self.get_language_title(title),
                )
                intermediate_language_objects.append(language)
            except Exception as e:
                logger.error(
                    f"Error {e} occurred while parsing intermediate language {title}"
                )

        activity_objects = []
        for activity_name in activities_data:
            try:
                activity, _ = Activity.objects.get_or_create(title=activity_name)
                activity_objects.append(activity)
            except Exception as e:
                logger.error(
                    f"Error {e} occurred while parsing activity {activity_name}"
                )

        skill_objects = []
        for skill_name in skills_data:
            try:
                skill, _ = Skill.objects.get_or_create(title=skill_name)
                skill_objects.append(skill)
            except Exception as e:
                logger.error(f"Error {e} occurred while parsing activity {skill_name}")

        volunteer_form = VolunteerForm.objects.create(**validated_data)
        volunteer_form.schedule.set(schedule_objects)
        volunteer_form.preferred_berlin_locations.set(location_objects)
        languages_for_m2m = (
            [
                VolunteerLanguageM2M(
                    volunteerform=volunteer_form,
                    language=language,
                    level=LanguageLevel.NATIVE,
                )
                for language in native_language_objects
            ]
            + [
                VolunteerLanguageM2M(
                    volunteerform=volunteer_form,
                    language=language,
                    level=LanguageLevel.FLUENT,
                )
                for language in fluent_language_objects
            ]
            + [
                VolunteerLanguageM2M(
                    volunteerform=volunteer_form,
                    language=language,
                    level=LanguageLevel.INTERMEDIATE,
                )
                for language in intermediate_language_objects
            ]
        )
        VolunteerLanguageM2M.objects.bulk_create(languages_for_m2m)
        volunteer_form.activities.set(activity_objects)
        volunteer_form.skills.set(skill_objects)

        return volunteer_form
