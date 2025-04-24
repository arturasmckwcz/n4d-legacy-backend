import structlog
from rest_framework import serializers

from alfred.settings import ENV
from alfred.slack_handler import slack_post_message
from data.enums import Environment, LanguageLevel
from data.models import (
    Activity,
    AuthEmailDomain,
    Avatar,
    BerlinLocation,
    Contact,
    FormLeadFrom,
    Language,
    LanguageTranslation,
    Location,
    Need4DeedDaySchedule,
    Opportunity,
    OpportunityTranslation,
    Organization,
    Person,
    Skill,
    Testimonial,
    Timeslot,
    VolunteerForm,
    VolunteerLanguage,
)
from data.utils import flatten_dict, is_test_case  # , is_valid_email
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


class Need4DeedDayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Need4DeedDaySchedule
        fields = [
            "day",
            "time_slot",
        ]


def get_language_obj(language: str) -> Language | None:
    """
    Retrieves a Language object based on the provided language identifier.

    This function attempts to find a Language object using either an ISO 639-1 (2-letter)
    or ISO 639-2/3 (3-letter) code, or by matching the language's title (or its translation).

    Args:
        language: The language identifier. It can be an ISO code (2 or 3 letters) or
                  the language's title (e.g., "English", "French", "Persian").

    Returns:
        The corresponding Language object if found, otherwise None.

    Raises:
        Exceptions during database queries are caught and logged, returning None.

    Note:
        The function handles a specific case where "Persian" is mapped to "Farsi"
        when searching by title.
    """

    def get_language_title(title: str) -> str:
        if title == "Persian":
            return "Farsi"
        return title

    if len(language) == 2 or len(language) == 3:
        try:
            return Language.objects.filter(iso_code=language).first()
        except Exception as e:
            logger.error(f"Error {e} occurred while parsing language {language}")
            return None

    try:
        translation = LanguageTranslation.objects.filter(
            title=get_language_title(language),
        ).first()
        if translation:
            return translation.language_obj
        return None
    except Exception as e:
        logger.error(f"Error {e} occurred while parsing language {language}")
        return None


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
    timeslots = serializers.SerializerMethodField(read_only=True)
    title = serializers.SerializerMethodField()
    vo_information = serializers.SerializerMethodField()
    accomp_information = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "vo_information",
            "accomp_information",
            "opportunity_type",
            "berlin_locations",
            "schedule_str",
            "datetime_str",
            "timeslots",
            "activities",
            "languages",
            "skills",
            "status",
            "opportunity_type",
            "accomp_datetime",
            "created_at",
            "updated_at",
        ]

    def get_timeslots(self, obj):
        timeslots = [
            Need4DeedDayScheduleSerializer(timeslot).data
            for timeslot in obj.timeslots.all()
        ]
        return timeslots

    def get_berlin_locations(self, obj):
        berlin_locations_details = [
            BerlinLocationSerializer(berlin_location).data
            for berlin_location in obj.berlin_locations.all()
        ]
        return berlin_locations_details

    def get_activities(self, obj):
        lang = self.context.get("language", "de")
        activities_details = [
            activity.get_title(lang) for activity in obj.activities.all()
        ]
        return activities_details

    def get_languages(self, obj):
        lang = self.context.get("language", "de")
        languages_details = [
            language.get_title(lang) for language in obj.languages.all()
        ]
        return languages_details

    def get_skills(self, obj):
        lang = self.context.get("language", "de")
        skills_details = [skill.get_title(lang) for skill in obj.skills.all()]
        return skills_details

    def get_title(self, obj):
        language_code = self.context.get("language", "de")
        return obj.get_title(language_code)

    def get_vo_information(self, obj):
        language_code = self.context.get("language", "de")
        return obj.get_vo_information(language_code)

    def get_accomp_information(self, obj):
        language_code = self.context.get("language", "de")
        return obj.get_accomp_information(language_code)

    def to_representation(self, instance):
        primary_keys = self.context.get("primary_keys", None)
        response = super().to_representation(instance)
        return flatten_dict(response, primary_keys)


class OpportunityCreateSerializer(serializers.ModelSerializer):
    language = serializers.CharField(write_only=True)
    berlin_locations = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    languages = serializers.ListField(child=serializers.CharField(), write_only=True)
    activities = serializers.ListField(child=serializers.CharField(), write_only=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    timeslots = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField()), write_only=True
    )
    title = serializers.CharField(write_only=True)
    vo_information = serializers.CharField(write_only=True, allow_blank=True)
    accomp_information = serializers.CharField(write_only=True, allow_blank=True)

    def validate_rac_email(self, value):
        _, domain = value.split("@")
        if not AuthEmailDomain.is_domain_authorized(domain.lower()):
            warning_msg = f"Attempt of unauthorized access from email: {value}."
            slack_post_message(warning_msg, dry_run=ENV != Environment.PRODUCTION)
            raise serializers.ValidationError(warning_msg)
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
        logger.debug(f"DEBUG: {validated_data=}")
        language_iso_code = validated_data.pop("language", None)
        logger.debug(f"DEBUG: {language_iso_code=}")
        title = validated_data.pop("title")
        vo_information = validated_data.pop("vo_information", "")
        accomp_information = validated_data.pop("accomp_information", "")
        berlin_locations_data = validated_data.pop("berlin_locations", [])

        original_language = Language.objects.filter(iso_code=language_iso_code).first()
        logger.debug(f"DEBUG: {original_language=}")

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
        for language_title in languages_data:
            language_obj = get_language_obj(language_title)
            if language_obj:
                languages.append(language_obj)

        timeslots_data = validated_data.pop("timeslots", [])
        timeslots = []
        for day, time_slot in timeslots_data:
            logger.debug(f"{day=}, {time_slot=}")
            day_number = int(day)
            timeslot_object, _ = Need4DeedDaySchedule.objects.get_or_create(
                day=day_number, time_slot=time_slot
            )
            timeslots.append(timeslot_object)

        opportunity_object = Opportunity.objects.create(**validated_data)

        opportunity_object.original_language = original_language
        logger.debug(f"DEBUG: {opportunity_object.original_language=}")
        opportunity_object.save()
        opportunity_object.berlin_locations.set(berlin_locations)
        opportunity_object.activities.set(activities)
        opportunity_object.skills.set(skills)
        opportunity_object.languages.set(languages)
        opportunity_object.timeslots.set(timeslots)
        OpportunityTranslation.objects.create(
            opportunity=opportunity_object,
            language=Language.objects.get(iso_code=language_iso_code or "zzz"),
            title=title,
            vo_information=vo_information,
            accomp_information=accomp_information,
        )

        slack_post_message(
            f"hey, please check the new opportunity {title} from {opportunity_object.rac_email}",
            dry_run=is_test_case(opportunity_object.rac_email),
        )

        return opportunity_object

    class Meta:
        model = Opportunity
        fields = (
            "title",
            "vo_information",
            "accomp_information",
            "opportunity_type",
            "accomp_datetime",
            "accomp_address",
            "accomp_postcode",
            "accomp_name",
            "accomp_phone",
            "rac_email",
            "rac_full_name",
            "rac_phone",
            "rac_address",
            "rac_plz",
            "volunteers_number",
            "berlin_locations",
            "languages",
            "activities",
            "skills",
            "timeslots",
            "id",
            "created_at",
            "language",
        )


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
        for language_title in native_languages_data:
            language_obj = get_language_obj(language_title)
            if language_obj:
                native_language_objects.append(language_obj)

        fluent_language_objects = []
        for language_title in fluent_languages_data:
            language_obj = get_language_obj(language_title)
            if language_obj:
                fluent_language_objects.append(language_obj)

        intermediate_language_objects = []
        for language_title in intermediate_languages_data:
            language_obj = get_language_obj(language_title)
            if language_obj:
                intermediate_language_objects.append(language_obj)

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
        volunteer_form.activities.set(activity_objects)
        volunteer_form.skills.set(skill_objects)

        languages_for_m2m = (
            [
                VolunteerLanguage(
                    volunteer_form=volunteer_form,
                    language=language,
                    level=LanguageLevel.NATIVE,
                )
                for language in native_language_objects
            ]
            + [
                VolunteerLanguage(
                    volunteer_form=volunteer_form,
                    language=language,
                    level=LanguageLevel.FLUENT,
                )
                for language in fluent_language_objects
            ]
            + [
                VolunteerLanguage(
                    volunteer_form=volunteer_form,
                    language=language,
                    level=LanguageLevel.INTERMEDIATE,
                )
                for language in intermediate_language_objects
            ]
        )
        VolunteerLanguage.objects.bulk_create(languages_for_m2m)

        email, phone = volunteer_form.check_email_and_phone()

        slack_post_message(
            f"hey, please check the new arrival to volunteers: {volunteer_form.email}{'\nWarning: '+email+' is already in use.' if email else ''}{'\nWarning: '+phone+' is already in use.' if phone else ''}",
            dry_run=is_test_case(volunteer_form.email),
        )

        return volunteer_form


class TestimonialSerializer(serializers.ModelSerializer):
    translated_text = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    def get_translated_text(self, obj):
        language_code = self.context.get("language", None)
        if not language_code:
            original_language_code = obj.original_language.iso_code
            language_code = original_language_code if original_language_code else "de"

        return obj.get_translated_text(language_code)

    def get_activities(self, obj):
        lang = self.context.get("language", "de")
        activities_details = [
            activity.get_title(lang) for activity in obj.activities.all()
        ]
        return activities_details

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.volunteer_form:
            name, *_ = obj.volunteer_form.full_name.split(" ")
            data["name"] = name

        return data

    class Meta:
        model = Testimonial
        fields = ("name", "pic", "translated_text", "activities")
