from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from notifications.services import create_notification
from .models import TeamMembership


@receiver(post_save, sender=TeamMembership, dispatch_uid="teamhub_notify_member_added_to_team")
def notify_member_added_to_team(sender, instance, created, raw, **kwargs):
    if raw or not created:
        return

    if (
        instance.user_id == instance.team.created_by_id
        and instance.role == TeamMembership.Role.OWNER
    ):
        return

    create_notification(
        recipient=instance.user,
        type=Notification.Type.TEAM_MEMBER_ADDED,
        title=f"You were added to {instance.team.name}",
        message=f"You were added as {instance.get_role_display()}.",
    )