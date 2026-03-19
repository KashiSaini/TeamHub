from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope["user"]

        if not user or not user.is_authenticated:
            self.close(code=4401)
            return

        self.group_name = f"user_{user.id}_notifications"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name,
        )

        self.accept()
        self.send_json({
            "type": "connection_established",
            "message": "WebSocket connected successfully.",
        })

    def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name,
            )

    def receive_json(self, content, **kwargs):
        if content.get("type") == "ping":
            self.send_json({"type": "pong"})

    def notification_message(self, event):
        self.send_json({
            "type": "notification",
            "data": event["notification"],
        })