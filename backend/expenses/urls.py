from rest_framework.routers import DefaultRouter

from .views import ExpenseViewSet
from .views import ExpenseParticipantViewSet

router = DefaultRouter()

router.register(
    r'expenses',
    ExpenseViewSet
)

router.register(
    r'expense-participants',
    ExpenseParticipantViewSet
)

urlpatterns = router.urls