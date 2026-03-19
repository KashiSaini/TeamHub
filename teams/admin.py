from django.contrib import admin
from .models import Team, TeamMembership, Project


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "team", "role", "joined_at")
    search_fields = ("user__username", "team__name")
    list_filter = ("role", "joined_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "team", "created_by", "created_at")
    search_fields = ("name", "team__name")
    list_filter = ("created_at",)