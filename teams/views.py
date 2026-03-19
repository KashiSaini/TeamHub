from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, filters
from rest_framework.exceptions import PermissionDenied

from .models import Team, TeamMembership, Project
from .permissions import (
    IsTeamMemberReadOnlyAdminOwnerWrite,
    is_team_admin_or_owner,
)
from .serializers import TeamSerializer, TeamMembershipSerializer, ProjectSerializer


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamMemberReadOnlyAdminOwnerWrite]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["created_by"]
    search_fields = ["name", "description", "created_by__username"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Team.objects.select_related("created_by").order_by("-created_at")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(members=self.request.user).distinct()

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        team = serializer.save(created_by=self.request.user)
        TeamMembership.objects.create(
            user=self.request.user,
            team=team,
            role=TeamMembership.Role.OWNER,
        )
        cache.clear()

    def perform_update(self, serializer):
        serializer.save()
        cache.clear()

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()


class TeamMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamMemberReadOnlyAdminOwnerWrite]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["team", "user", "role"]
    search_fields = ["user__username", "team__name"]
    ordering_fields = ["joined_at", "role"]
    ordering = ["-joined_at"]

    def get_queryset(self):
        queryset = TeamMembership.objects.select_related("user", "team").order_by("-joined_at")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(team__members=self.request.user).distinct()

    def perform_create(self, serializer):
        team = serializer.validated_data["team"]
        if not is_team_admin_or_owner(self.request.user, team):
            raise PermissionDenied("Only team owners or admins can add members.")
        serializer.save()

    def perform_update(self, serializer):
        team = serializer.instance.team
        if not is_team_admin_or_owner(self.request.user, team):
            raise PermissionDenied("Only team owners or admins can update memberships.")
        serializer.save()

    def perform_destroy(self, instance):
        if not is_team_admin_or_owner(self.request.user, instance.team):
            raise PermissionDenied("Only team owners or admins can remove members.")
        instance.delete()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamMemberReadOnlyAdminOwnerWrite]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["team", "created_by"]
    search_fields = ["name", "description", "team__name", "created_by__username"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Project.objects.select_related("team", "created_by").order_by("-created_at")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(team__members=self.request.user).distinct()

    def perform_create(self, serializer):
        team = serializer.validated_data["team"]
        if not is_team_admin_or_owner(self.request.user, team):
            raise PermissionDenied("Only team owners or admins can create projects.")
        serializer.save(created_by=self.request.user)