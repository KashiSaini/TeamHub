from rest_framework import serializers
from teams.models import TeamMembership
from .models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source="created_by.username")
    assigned_to_username = serializers.ReadOnlyField(source="assigned_to.username")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_name",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_username",
            "created_by",
            "created_by_username",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))

        if project and assigned_to:
            is_member = TeamMembership.objects.filter(
                team=project.team,
                user=assigned_to,
            ).exists()
            if not is_member:
                raise serializers.ValidationError(
                    {"assigned_to": "Assigned user must be a member of this task's team."}
                )

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source="author.username")
    task_title = serializers.ReadOnlyField(source="task.title")

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "task_title",
            "author",
            "author_username",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "created_at", "updated_at"]