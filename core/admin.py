from django.contrib import admin

from .models import (
    Project,
    Responsibility,
    DataEntry,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "domain",
        "coordinator",
        "status",
        "start_date",
    )

    list_filter = (
        "status",
        "domain",
    )

    search_fields = (
        "name",
        "domain",
        "coordinator__first_name",
        "coordinator__last_name",
    )


@admin.register(Responsibility)
class ResponsibilityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "responsible",
        "support",
        "frequency",
        "active",
    )

    list_filter = (
        "active",
        "project",
    )

    search_fields = (
        "name",
        "responsible__first_name",
        "responsible__last_name",
    )


@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = (
        "responsibility",
        "created_by",
        "updated_at",
        "archived",
    )

    list_filter = (
        "archived",
        "created_at",
        "responsibility",
    )

    search_fields = (
        "responsibility__name",
        "notes",
    )