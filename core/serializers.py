from rest_framework import serializers

from .models import Project, Responsibility, DataEntry
from .models import Project, Responsibility, DataEntry, InitialState

class DataEntrySerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    responsibility_name = serializers.CharField(
        source="responsibility.name",
        read_only=True,
    )

    class Meta:
        model = DataEntry
        fields = [
            "id",
            "responsibility",
            "responsibility_name",
            "entry_date",
            "action_date",
            "data",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "archived",
        ]
        read_only_fields = [
            "created_by",
            "created_by_name",
            "responsibility_name",
            "entry_date",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.full_name()


class ProjectSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.SerializerMethodField()
    responsibilities_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "domain",
            "description",
            "coordinator",
            "coordinator_name",
            "start_date",
            "end_date",
            "status",
            "responsibilities_count",
            "created_at",
            "updated_at",
        ]

    def get_coordinator_name(self, obj):
        return obj.coordinator.full_name()

    def get_responsibilities_count(self, obj):
        return obj.responsibilities.filter(active=True).count()



class ResponsibilitySerializer(serializers.ModelSerializer):
    responsible_name = serializers.SerializerMethodField()
    support_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    class Meta:
        model = Responsibility
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "responsible",
            "responsible_name",
            "support",
            "support_name",
            "frequency",
            "proof_required",
            "form_schema",
            "active",
        ]

    def get_responsible_name(self, obj):
        if obj.responsible:
            return obj.responsible.full_name()
        return ""

    def get_support_name(self, obj):
        if obj.support:
            return obj.support.full_name()
        return ""


class InitialStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialState
        fields = [
            "id",
            "responsibility",
            "data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]