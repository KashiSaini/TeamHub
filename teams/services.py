from django.core.cache import cache
from teams.models import Team, Project
from tasks.models import Task


def get_user_dashboard_summary(user):
    cache_key = f"user_dashboard_summary:{user.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = {
        "teams_count": Team.objects.filter(members=user).distinct().count(),
        "projects_count": Project.objects.filter(team__members=user).distinct().count(),
        "assigned_tasks_count": Task.objects.filter(assigned_to=user).count(),
        "open_tasks_count": Task.objects.filter(
            project__team__members=user,
            status__in=["todo", "in_progress"],
        ).distinct().count(),
    }

    cache.set(cache_key, data, timeout=120)
    return data