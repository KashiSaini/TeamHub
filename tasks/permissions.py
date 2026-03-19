from rest_framework import permissions
from teams.permissions import is_team_member, is_team_admin_or_owner


class IsTaskReadableByTeamMemberEditableByStakeholders(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        team = obj.project.team

        if not is_team_member(request.user, team):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if is_team_admin_or_owner(request.user, team):
            return True

        return obj.created_by_id == request.user.id or obj.assigned_to_id == request.user.id


class IsCommentReadableByTeamMemberEditableByAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        team = obj.task.project.team

        if not is_team_member(request.user, team):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if is_team_admin_or_owner(request.user, team):
            return True

        return obj.author_id == request.user.id