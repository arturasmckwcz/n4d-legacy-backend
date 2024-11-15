from django.contrib import admin

from data.models import (
    Activity,
    Avatar,
    BerlinLocation,
    Contact,
    FormLeadFrom,
    Language,
    Location,
    Opportunity,
    Organization,
    Person,
    Skill,
    VolunteerForm,
)


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


@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    search_fields = ("email", "full_name")
