import secrets
from django.core.cache import cache


def create_team_invite_token(team_id):
    token = secrets.token_urlsafe(24)
    cache_key = f"team_invite:{token}"
    cache.set(cache_key, str(team_id), timeout=600)
    return token


def get_team_id_from_invite_token(token):
    cache_key = f"team_invite:{token}"
    return cache.get(cache_key)


def consume_team_invite_token(token):
    cache_key = f"team_invite:{token}"
    team_id = cache.get(cache_key)
    if team_id:
        cache.delete(cache_key)
    return team_id