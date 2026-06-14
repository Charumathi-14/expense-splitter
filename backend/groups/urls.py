from rest_framework.routers import DefaultRouter

from .views import GroupViewSet, GroupMemberViewSet

router = DefaultRouter()
router.register('groups', GroupViewSet)
router.register('group-members', GroupMemberViewSet)

urlpatterns = router.urls