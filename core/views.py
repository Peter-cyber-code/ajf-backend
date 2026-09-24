from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, Responsibility, DataEntry, InitialState

from .models import Project, Responsibility, DataEntry
from .serializers import (
    ProjectSerializer,
    ResponsibilitySerializer,
    DataEntrySerializer,
    InitialStateSerializer
)


class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = ProjectSerializer


class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectResponsibilitiesView(generics.ListAPIView):
    serializer_class = ResponsibilitySerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]

        return Responsibility.objects.filter(
            project_id=project_id,
            active=True,
        ).select_related(
            "project",
            "responsible",
        )


class ResponsibilityEntriesView(generics.ListAPIView):
    serializer_class = DataEntrySerializer

    def get_queryset(self):
        responsibility_id = self.kwargs["responsibility_id"]

        return DataEntry.objects.filter(
            responsibility_id=responsibility_id,
        ).select_related(
            "created_by",
            "responsibility",
        ).order_by(
            "-entry_date",
            "-created_at",
        )


class ProjectEntriesView(generics.ListAPIView):
    serializer_class = DataEntrySerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]

        queryset = DataEntry.objects.filter(
            responsibility__project_id=project_id,
        ).select_related(
            "created_by",
            "responsibility",
            "responsibility__project",
        )

        # ---------------------------------------------------------
        # 1. Filtre archivage
        # ---------------------------------------------------------

        archived = self.request.query_params.get("archived")

        if archived == "true":
            queryset = queryset.filter(archived=True)
        else:
            # Par défaut, on affiche uniquement les données actives
            queryset = queryset.filter(archived=False)

        # ---------------------------------------------------------
        # 2. Filtre par responsabilité / catégorie
        # ---------------------------------------------------------

        responsibility_id = self.request.query_params.get(
            "responsibility_id"
        )

        if responsibility_id:
            queryset = queryset.filter(
                responsibility_id=responsibility_id
            )

        # ---------------------------------------------------------
        # 3. Filtre par période
        # ---------------------------------------------------------

        period = self.request.query_params.get("period")

        from django.utils import timezone
        from datetime import timedelta

        today = timezone.localdate()

        if period == "today":
            queryset = queryset.filter(
                entry_date=today
            )

        elif period == "week":
            start_of_week = today - timedelta(
                days=today.weekday()
            )

            queryset = queryset.filter(
                entry_date__gte=start_of_week,
                entry_date__lte=today,
            )

        elif period == "month":
            start_of_month = today.replace(day=1)

            queryset = queryset.filter(
                entry_date__gte=start_of_month,
                entry_date__lte=today,
            )

        elif period == "3months":
            start_date = today - timedelta(days=90)

            queryset = queryset.filter(
                entry_date__gte=start_date,
                entry_date__lte=today,
            )

        return queryset.order_by(
            "-entry_date",
            "-created_at",
        )


class CreateDataEntryView(generics.CreateAPIView):
    serializer_class = DataEntrySerializer

    def create(self, request, *args, **kwargs):
        responsibility_id = kwargs["responsibility_id"]
        user_id = request.data.get("user_id")

        # ---------------------------------------------------------
        # 1. Vérification de l'utilisateur
        # ---------------------------------------------------------

        if not user_id:
            return Response(
                {
                    "success": False,
                    "message": "Utilisateur requis.",
                },
                status=400,
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return Response(
                {
                    "success": False,
                    "message": "Identifiant utilisateur invalide.",
                },
                status=400,
            )

        # ---------------------------------------------------------
        # 2. Récupération de la responsabilité
        # ---------------------------------------------------------

        responsibility = (
            Responsibility.objects
            .select_related("responsible")
            .filter(
                id=responsibility_id,
                active=True,
            )
            .first()
        )

        if responsibility is None:
            return Response(
                {
                    "success": False,
                    "message": "Responsabilité introuvable.",
                },
                status=404,
            )

        # ---------------------------------------------------------
        # 3. Vérification que l'utilisateur est bien
        #    le responsable de cette responsabilité
        # ---------------------------------------------------------

        if responsibility.responsible_id != user_id:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Cet utilisateur n'est pas le "
                        "responsable de cette responsabilité."
                    ),
                },
                status=403,
            )

        # ---------------------------------------------------------
        # 4. Validation des données
        # ---------------------------------------------------------

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ---------------------------------------------------------
        # 5. Enregistrement
        # ---------------------------------------------------------

        serializer.save(
            created_by=responsibility.responsible
        )

        return Response(
            {
                "success": True,
                "message": "Donnée enregistrée avec succès.",
                "entry": serializer.data,
            },
            status=201,
        )

class ResponsibilityAccessView(APIView):

    def post(self, request):
        project_id = request.data.get("project_id")
        access_code = request.data.get("access_code")

        if not project_id or not access_code:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Le projet et le code personnel sont requis."
                    ),
                },
                status=400,
            )

        # ---------------------------------------------------------
        # 1. Rechercher le membre grâce à son code personnel
        # ---------------------------------------------------------

        from django.contrib.auth import get_user_model
        from django.db import models

        User = get_user_model()

        user = (
            User.objects
            .filter(
                access_code=str(access_code).strip(),
                is_active=True,
                is_active_member=True,
            )
            .first()
        )

        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Code personnel incorrect.",
                },
                status=401,
            )

        # ---------------------------------------------------------
        # 2. Vérifier que le projet existe
        # ---------------------------------------------------------

        project = (
            Project.objects
            .filter(id=project_id)
            .select_related("coordinator")
            .first()
        )

        if project is None:
            return Response(
                {
                    "success": False,
                    "message": "Projet introuvable.",
                },
                status=404,
            )

        # ---------------------------------------------------------
        # 3. Vérifier si le membre est coordinateur
        # ---------------------------------------------------------

        is_coordinator = (
            project.coordinator_id == user.id
        )

        # ---------------------------------------------------------
        # 4. Récupérer les responsabilités selon le type d'accès
        # ---------------------------------------------------------

        if is_coordinator:

            # Le coordinateur voit TOUTES les responsabilités
            # actives du projet.
            responsibilities_queryset = (
                Responsibility.objects
                .filter(
                    project=project,
                    active=True,
                )
                .select_related(
                    "project",
                    "responsible",
                    "support",
                )
                .order_by("name")
            )

        else:

            # Un membre normal ne voit que les responsabilités
            # auxquelles il est affecté comme responsable ou appui.
            responsibilities_queryset = (
                Responsibility.objects
                .filter(
                    project=project,
                    active=True,
                )
                .filter(
                    models.Q(responsible=user)
                    | models.Q(support=user)
                )
                .select_related(
                    "project",
                    "responsible",
                    "support",
                )
                .order_by("name")
            )

        # ---------------------------------------------------------
        # 5. Le membre doit avoir au moins un accès au projet
        # ---------------------------------------------------------

        if (
            not is_coordinator
            and not responsibilities_queryset.exists()
        ):
            return Response(
                {
                    "success": False,
                    "message": (
                        "Ce membre n'a aucun accès "
                        "à ce projet."
                    ),
                },
                status=403,
            )

        # ---------------------------------------------------------
        # 6. Informations générales du membre
        # ---------------------------------------------------------

        full_name = (
            f"{user.first_name} {user.last_name}"
        ).strip()

        if not full_name:
            full_name = user.username

        # ---------------------------------------------------------
        # 7. Construire la liste des responsabilités
        # ---------------------------------------------------------

        responsibilities = []

        for item in responsibilities_queryset:

            # Déterminer le type d'accès
            if is_coordinator:
                access_type = "coordinator"

            elif item.responsible_id == user.id:
                access_type = "responsible"

            else:
                access_type = "support"

            responsibilities.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "frequency": item.frequency,
                    "proof_required": item.proof_required,
                    "form_schema": item.form_schema,
                    "active": item.active,

                    "access_type": access_type,

                    "responsible_id": item.responsible_id,
                    "responsible_name": (
                        item.responsible.full_name()
                        if item.responsible
                        else ""
                    ),

                    "support_id": item.support_id,
                    "support_name": (
                        item.support.full_name()
                        if item.support
                        else ""
                    ),
                }
            )

        # ---------------------------------------------------------
        # 8. Réponse envoyée à Flutter
        # ---------------------------------------------------------

        return Response(
            {
                "success": True,

                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": full_name,
                    "phone": user.phone,
                },

                "project": {
                    "id": project.id,
                    "name": project.name,
                    "domain": project.domain,
                },

                "access": {
                    "is_coordinator": is_coordinator,
                    "role": (
                        "coordinator"
                        if is_coordinator
                        else "member"
                    ),
                },

                "responsibilities": responsibilities,
            },
            status=200,
        )


class ResponsibilityInitialStateView(APIView):

    def get(self, request, responsibility_id):
        responsibility = (
            Responsibility.objects
            .filter(
                id=responsibility_id,
                active=True,
            )
            .select_related("project", "responsible")
            .first()
        )

        if responsibility is None:
            return Response(
                {
                    "success": False,
                    "message": "Responsabilité introuvable.",
                },
                status=404,
            )

        initial_state = (
            InitialState.objects
            .filter(responsibility=responsibility)
            .first()
        )

        # Aucun état initial configuré
        if initial_state is None:
            return Response(
                {
                    "success": True,
                    "configured": False,
                    "responsibility": responsibility.id,
                    "responsibility_name": responsibility.name,
                    "data": {},
                },
                status=200,
            )

        serializer = InitialStateSerializer(initial_state)

        return Response(
            {
                "success": True,
                "configured": True,
                "responsibility": responsibility.id,
                "responsibility_name": responsibility.name,
                "state": serializer.data,
            },
            status=200,
        )

    def post(self, request, responsibility_id):

        responsibility = (
            Responsibility.objects
            .filter(
                id=responsibility_id,
                active=True,
            )
            .select_related("responsible")
            .first()
        )

        if responsibility is None:
            return Response(
                {
                    "success": False,
                    "message": "Responsabilité introuvable.",
                },
                status=404,
            )

        # --------------------------------------------------
        # Vérification du responsable
        # --------------------------------------------------

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {
                    "success": False,
                    "message": "Utilisateur requis.",
                },
                status=400,
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return Response(
                {
                    "success": False,
                    "message": "Identifiant utilisateur invalide.",
                },
                status=400,
            )

        if responsibility.responsible_id != user_id:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Cet utilisateur n'est pas "
                        "le responsable de cette responsabilité."
                    ),
                },
                status=403,
            )

        # --------------------------------------------------
        # Vérification des données
        # --------------------------------------------------

        data = request.data.get("data")

        if not isinstance(data, dict):
            return Response(
                {
                    "success": False,
                    "message": (
                        "Les données initiales doivent "
                        "être un objet."
                    ),
                },
                status=400,
            )

        # --------------------------------------------------
        # Création ou mise à jour
        # --------------------------------------------------

        initial_state, created = (
            InitialState.objects.update_or_create(
                responsibility=responsibility,
                defaults={
                    "data": data,
                },
            )
        )

        serializer = InitialStateSerializer(
            initial_state
        )

        return Response(
            {
                "success": True,
                "created": created,
                "message": (
                    "État initial enregistré avec succès."
                    if created
                    else "État initial mis à jour avec succès."
                ),
                "state": serializer.data,
            },
            status=201 if created else 200,
        )


class MemberAccessView(APIView):

    def post(self, request):
        access_code = request.data.get("access_code")

        if not access_code:
            return Response(
                {
                    "success": False,
                    "message": "Le code personnel est requis.",
                },
                status=400,
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = (
            User.objects
            .filter(
                access_code=str(access_code).strip(),
                is_active=True,
                is_active_member=True,
            )
            .first()
        )

        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Code personnel incorrect ou membre non actif.",
                },
                status=401,
            )

        full_name = (
            f"{user.first_name} {user.last_name}"
        ).strip()

        if not full_name:
            full_name = user.username

        return Response(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": full_name,
                    "phone": user.phone,
                },
            },
            status=200,
        )