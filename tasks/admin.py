from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "status", "priority", "assigned_to", "created_at")
    search_fields = ("title", "project__name")
    list_filter = ("status", "priority", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    search_fields = ("task__title", "author__username")
    list_filter = ("created_at",)