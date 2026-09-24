from django.contrib import admin
from .models import Member, Role
from django.contrib.auth.admin import UserAdmin

from .models import Member, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "phone",
        "access_code",
        "association_role",
        "is_active_member",
        "is_active",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "phone",
        "access_code",
    )

    list_filter = (
        "is_active_member",
        "is_active",
        "association_role",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informations AJF",
            {
                "fields": (
                    "phone",
                    "access_code",
                    "association_role",
                    "is_active_member",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informations AJF",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "access_code",
                    "association_role",
                    "is_active_member",
                ),
            },
        ),
    )

