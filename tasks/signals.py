from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from notifications.services import create_notification
from .models import Task, Comment


@receiver(post_save, sender=Task, dispatch_uid="teamhub_notify_task_assigned_on_create")
def notify_task_assigned_on_create(sender, instance, created, raw, **kwargs):
    if raw or not created:
        return

    if not instance.assigned_to_id:
        return

    if instance.assigned_to_id == instance.created_by_id:
        return

    create_notification(
        recipient=instance.assigned_to,
        type=Notification.Type.TASK_ASSIGNED,
        title=f"You were assigned a task: {instance.title}",
        message=f"Task '{instance.title}' was assigned to you in project '{instance.project.name}'.",
    )


@receiver(post_save, sender=Comment, dispatch_uid="teamhub_notify_comment_added")
def notify_comment_added(sender, instance, created, raw, **kwargs):
    if raw or not created:
        return

    recipients = []

    if instance.task.created_by_id != instance.author_id:
        recipients.append(instance.task.created_by)

    if (
        instance.task.assigned_to_id
        and instance.task.assigned_to_id != instance.author_id
        and instance.task.assigned_to_id != instance.task.created_by_id
    ):
        recipients.append(instance.task.assigned_to)

    for user in recipients:
        create_notification(
            recipient=user,
            type=Notification.Type.COMMENT_ADDED,
            title=f"New comment on task: {instance.task.title}",
            message=f"{instance.author.username} commented: {instance.content[:100]}",
        )