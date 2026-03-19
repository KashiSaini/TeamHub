from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(*, recipient, type, title, message):
    notification = Notification.objects.create(
        recipient=recipient,
        type=type,
        title=title,
        message=message,
    )

    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}_notifications",
            {
                "type": "notification.message",
                "notification": {
                    "id": notification.id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )

    return notification