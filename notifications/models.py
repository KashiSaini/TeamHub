from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        TEAM_MEMBER_ADDED = "team_member_added", "Team Member Added"
        TASK_ASSIGNED = "task_assigned", "Task Assigned"
        COMMENT_ADDED = "comment_added", "Comment Added"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(
        max_length=50,
        choices=Type.choices,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"