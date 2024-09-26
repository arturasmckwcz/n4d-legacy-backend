from django.contrib import admin

from data.models import (
    Avatar,
    Contact,
    Language,
    Location,
    Opportunity,
    Organization,
    Person,
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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    pass


@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    pass
