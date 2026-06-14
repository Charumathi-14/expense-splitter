from django.urls import path

from .views import GroupBalanceView

urlpatterns = [
    path('groups/<int:group_id>/balance/', GroupBalanceView.as_view(), name='group-balance'),
]
