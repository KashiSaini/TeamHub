from rest_framework import permissions
from .models import Team, TeamMembership


def is_team_member(user, team):
    if not user or not user.is_authenticated:
        return False
    return TeamMembership.objects.filter(user=user, team=team).exists()


def is_team_admin_or_owner(user, team):
    if not user or not user.is_authenticated:
        return False
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        role__in=[TeamMembership.Role.OWNER, TeamMembership.Role.ADMIN],
    ).exists()


class IsTeamMemberReadOnlyAdminOwnerWrite(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        team = obj if isinstance(obj, Team) else obj.team

        if request.method in permissions.SAFE_METHODS:
            return is_team_member(request.user, team)

        return is_team_admin_or_owner(request.user, team)