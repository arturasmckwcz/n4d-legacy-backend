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
    OpportunityTranslation,
    Organization,
    Person,
    Skill,
    VolunteerForm,
)


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
    search_fields = ("title", "status")
    inlines = [OpportunityTranslationInline]

    def title_display(self, obj):
        return obj.get_title()

    title_display.short_description = "Title"
    list_display = ["title_display", "rac_email"]

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
            if not any(
                instance.language.iso_code == "de" and instance.title
                for instance in instances
            ):
                raise ValidationError("German title is required")
        formset.save()


@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    search_fields = ("email", "full_name")
