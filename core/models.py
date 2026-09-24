from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "En cours"),
        ("COMPLETED", "Terminé"),
        ("PAUSED", "En pause"),
    ]

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=150, default="Élevage")
    description = models.TextField(blank=True)

    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coordinated_projects",
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Responsibility(models.Model):
    """
    Une responsabilité dans un projet.

    Exemple pour l'élevage :
    - Gestion alimentaire
    - Santé
    - Production
    - Recherche de clients et vente
    - Finance / comptabilité
    - Communication
    - Veille élevage
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="responsibilities",
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="responsibilities",
    )

    support = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="supported_responsibilities",
        null=True,
        blank=True,
    )

    frequency = models.CharField(
        max_length=100,
        blank=True,
    )

    proof_required = models.CharField(
        max_length=200,
        blank=True,
    )

    form_schema = models.JSONField (
        max_length=200,
        blank=True
    )

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class InitialState(models.Model):
    """
    État initial d'une responsabilité au moment
    où le projet commence à être suivi dans l'application.
    """

    responsibility = models.OneToOneField(
        Responsibility,
        on_delete=models.CASCADE,
        related_name="initial_state",
    )

    data = models.JSONField(
        default=dict,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"État initial - {self.responsibility.name}"

class DataEntry(models.Model):

    responsibility = models.ForeignKey(
        Responsibility,
        on_delete=models.CASCADE,
        related_name="entries",
    )

    entry_date = models.DateField(
        auto_now_add=True,
    )

    action_date = models.DateField(
        null=True,
        blank=True,
    )

    data = models.JSONField(
        default=dict,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="data_entries",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    archived = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.responsibility.name} - {self.entry_date}"