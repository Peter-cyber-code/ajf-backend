from django.urls import path

from .views import (
    ProjectListView,
    ProjectDetailView,
    ProjectResponsibilitiesView,
    ResponsibilityEntriesView,
    CreateDataEntryView,
    ResponsibilityAccessView,
    ProjectEntriesView,
    ResponsibilityInitialStateView,
    MemberAccessView,
)


urlpatterns = [
    path(
        "projects/",
        ProjectListView.as_view(),
        name="project-list",
    ),

    path(
        "projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),

    path(
        "projects/<int:project_id>/responsibilities/",
        ProjectResponsibilitiesView.as_view(),
        name="project-responsibilities",
    ),

    path(
        "responsibility-access/",
        ResponsibilityAccessView.as_view(),
        name="responsibility-access",
    ),

    path(
        "responsibilities/<int:responsibility_id>/entries/",
        ResponsibilityEntriesView.as_view(),
        name="responsibility-entries",
    ),

    path(
        "responsibilities/<int:responsibility_id>/entries/create/",
        CreateDataEntryView.as_view(),
        name="data-entry-create",
    ),

    path(
        "projects/<int:project_id>/entries/",
        ProjectEntriesView.as_view(),
        name="project-entries",
    ),

    path(
        "responsibilities/<int:responsibility_id>/initial-state/",
        ResponsibilityInitialStateView.as_view(),
        name="responsibility-initial-state",
    ),

    path(
        "member-access/",
        MemberAccessView.as_view(),
        name="member-access",
    ),
]