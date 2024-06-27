from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import AlfredUser


@admin.register(AlfredUser)
class AlfredUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("user_type",)},
        ),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)
