import structlog
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from data.models import (
    Activity,
    AuthEmailDomain,
    Avatar,
    BerlinLocation,
    Contact,
    FormLeadFrom,
    Language,
    Location,
    Opportunity,
    OpportunityTranslation,
    Organization,
    Person,
    Skill,
    Testimonial,
    TitleTranslation,
    VolunteerForm,
    VolunteerLanguage,
)

logger = structlog.get_logger(__name__)


class TranslationInlineFormSet(BaseInlineFormSet):
    pass


class OpportunityTranslationInline(admin.TabularInline):
    model = OpportunityTranslation
    extra = 1
    formset = TranslationInlineFormSet
    fields = ["language", "title", "accomp_information", "vo_information"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ("iso_code", "title")


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    pass


@admin.register(FormLeadFrom)
class LeadAdmin(admin.ModelAdmin):
    pass


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(BerlinLocation)
class BerlinLocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(AuthEmailDomain)
class AuthEmailDomainAdmin(admin.ModelAdmin):
    pass


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    pass


@admin.register(TitleTranslation)
class TitleTranslationAdmin(admin.ModelAdmin):
    search_fields = ["language__iso_code", "translation", "content_type__model"]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    inlines = [OpportunityTranslationInline]
    search_fields = ["notion_id", "rac_email", "translations__title"]

    def title_display(self, obj):
        iso_code = obj.original_language.iso_code if obj.original_language else "de"
        return obj.get_title(iso_code)

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def updated_at_display(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    def last_edited_time_notion_display(self, obj):
        return obj.last_edited_time_notion.strftime("%Y-%m-%d %H:%M")

    title_display.short_description = "Title"
    title_display.admin_order_field = "translations__title"
    created_at_display.short_description = "Created At"
    created_at_display.admin_order_field = "created_at"
    updated_at_display.short_description = "Updated At"
    updated_at_display.admin_order_field = "updated_at"
    last_edited_time_notion_display.short_desription = "L.E.T. Notion"
    last_edited_time_notion_display.admin_order_field = "last_edited_time_notion"

    list_display = [
        "title_display",
        "rac_email",
        "created_at_display",
        "updated_at_display",
        "last_edited_time_notion",
    ]


class VolunteerLanguageInline(admin.TabularInline):
    model = VolunteerLanguage
    extra = 1


@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    inlines = [VolunteerLanguageInline]
    search_fields = (
        "email",
        "full_name",
        "languages__language__title",
        "languages__language__iso_code",
    )
    list_display = (
        "full_name",
        "email",
        "notion_id",
        "last_edited_time_notion",
        "get_languages_display",
    )

    def get_languages_display(self, obj):
        languages = obj.languages.all()
        return ", ".join([f"{lan.language.title} ({lan.level})" for lan in languages])

    get_languages_display.short_description = "Languages"

    def last_edited_time_notion_display(self, obj):
        if obj.last_edited_time_notion:
            return obj.last_edited_time_notion.strftime("%Y-%m-%d %H:%M")
        return "-"

    last_edited_time_notion_display.short_description = "L.E.T. Notion"
    last_edited_time_notion_display.admin_order_field = "last_edited_time_notion"


@admin.register(VolunteerLanguage)
class VolunteerLanguageAdmin(admin.ModelAdmin):
    list_display = ("volunteer_form", "language", "level")
    list_filter = ("level", "language")
    search_fields = (
        "volunteer_form__full_name",
        "volunteer_form__email",
        "language__title",
    )
