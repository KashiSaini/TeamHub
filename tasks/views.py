from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from teams.permissions import is_team_member
from .models import Task, Comment
from .permissions import (
    IsTaskReadableByTeamMemberEditableByStakeholders,
    IsCommentReadableByTeamMemberEditableByAuthorOrAdmin,
)
from .serializers import TaskSerializer, CommentSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskReadableByTeamMemberEditableByStakeholders]

    def get_queryset(self):
        queryset = Task.objects.select_related(
            "project",
            "project__team",
            "assigned_to",
            "created_by",
        ).order_by("-created_at")

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(project__team__members=self.request.user).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if not is_team_member(self.request.user, project.team):
            raise PermissionDenied("You must be a member of the team to create tasks in this project.")

        serializer.save(created_by=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentReadableByTeamMemberEditableByAuthorOrAdmin]

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "task",
            "task__project",
            "task__project__team",
            "author",
        ).order_by("-created_at")

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(task__project__team__members=self.request.user).distinct()

    def perform_create(self, serializer):
        task = serializer.validated_data["task"]

        if not is_team_member(self.request.user, task.project.team):
            raise PermissionDenied("You must be a member of the team to comment on this task.")

        serializer.save(author=self.request.user)