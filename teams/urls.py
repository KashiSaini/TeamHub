from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamMembershipViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"memberships", TeamMembershipViewSet, basename="membership")
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = router.urls