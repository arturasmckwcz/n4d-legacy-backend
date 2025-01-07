import structlog
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from data.models import (
    Activity,
    Avatar,
    BerlinLocation,
    Contact,
    FormLeadFrom,
    Language,
    Location,
    Opportunity,
    OpportunityLanguageM2M,
    OpportunityTranslation,
    Organization,
    Person,
    Skill,
    VolunteerForm,
)

logger = structlog.get_logger(__name__)


class OpportunityTranslationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """
        Check that at least one German translation with title exists.
        """
        super().clean()
        has_german_title = any(
            form.cleaned_data.get("language")
            and form.cleaned_data.get("language").iso_code == "de"
            and form.cleaned_data.get("title")
            for form in self.forms
            if not form.cleaned_data.get("DELETE", False)
        )
        if not has_german_title:
            raise ValidationError("Please provide a German title for the opportunity.")


class OpportunityTranslationInline(admin.TabularInline):
    model = OpportunityTranslation
    extra = 1
    formset = OpportunityTranslationInlineFormSet
    fields = ["language", "title", "accomp_information", "vo_information"]


class OpportunityLanguageInline(admin.TabularInline):  # or admin.StackedInline
    model = OpportunityLanguageM2M
    extra = 1


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


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    inlines = [OpportunityTranslationInline, OpportunityLanguageInline]
    search_fields = ["notion_id", "rac_email", "translations__title"]

    def title_display(self, obj):
        return obj.get_title()

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

    def save_model(self, request, obj, form, change):
        """
        In Django admin, when you have an inline formset (like our OpportunityTranslationInline),
        Django automatically generates form field names following this pattern:
        {inline_prefix}-{index}-{field_name}

        Where:
        - translations is the related_name from your model relationship (from Opportunity to OpportunityTranslation)
        - 0 is the index of the first inline form (they start at 0)
        - title is the field name in your OpportunityTranslation model
        """
        if not change:
            if not any(
                "translations-0-title" in k and v for k, v in request.POST.items()
            ):
                raise ValidationError("German title is required")
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == OpportunityTranslation:
            instances = formset.save(commit=False)
            has_german = any(
                instance.language.iso_code == "de" and instance.title
                for instance in instances
            )
            if change and not has_german:
                has_german = formset.instance.translations.filter(
                    language__iso_code="de", title__isnull=False
                ).exists()
            if not has_german:
                raise ValidationError("German title is required")
        formset.save()


@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    search_fields = ("email", "full_name")
