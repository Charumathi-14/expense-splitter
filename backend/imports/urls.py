from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ImportUploadView
from .views import ImportBatchViewSet, ImportIssueViewSet

router = DefaultRouter()
router.register('import-batches', ImportBatchViewSet)
router.register('import-issues', ImportIssueViewSet)

urlpatterns = [
    path('imports/run/', ImportUploadView.as_view(), name='import-run'),
] + router.urls
