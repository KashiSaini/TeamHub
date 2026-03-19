from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app
        self.jwt_auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        query_string = parse_qs(scope["query_string"].decode())
        raw_token = query_string.get("token", [None])[0]

        if raw_token:
            try:
                validated_token = self.jwt_auth.get_validated_token(raw_token)
                user = await database_sync_to_async(self.jwt_auth.get_user)(validated_token)
                scope["user"] = user
            except (InvalidToken, TokenError):
                scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)