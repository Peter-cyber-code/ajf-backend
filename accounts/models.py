from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    Rôle général du membre au sein de l'AJF.
    Exemples :
    - Président
    - Chargé de finances
    - Secrétaire
    - Informaticien
    - Membre
    """

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Member(AbstractUser):
    """
    Membre de l'AJF.

    Le même utilisateur pourra :
    - être simple membre ;
    - être coordinateur d'un projet ;
    - être responsable d'une tâche ;
    - avoir un rôle général dans l'association.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    access_code = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    association_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )

    is_active_member = models.BooleanField(
        default=True,
    )

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name() or self.username