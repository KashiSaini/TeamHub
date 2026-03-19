from rest_framework import serializers
from .models import Team, TeamMembership, Project


class TeamMembershipSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source="user.username")
    team_name = serializers.ReadOnlyField(source="team.name")

    class Meta:
        model = TeamMembership
        fields = [
            "id",
            "user",
            "user_username",
            "team",
            "team_name",
            "role",
            "joined_at",
        ]
        read_only_fields = ["joined_at"]

    def validate(self, attrs):
        user = attrs["user"]
        team = attrs["team"]

        qs = TeamMembership.objects.filter(user=user, team=team)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("This user is already a member of this team.")

        return attrs


class TeamSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class ProjectSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source="created_by.username")
    team_name = serializers.ReadOnlyField(source="team.name")

    class Meta:
        model = Project
        fields = [
            "id",
            "team",
            "team_name",
            "name",
            "description",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]