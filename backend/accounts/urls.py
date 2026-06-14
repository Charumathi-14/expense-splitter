from django.urls import path
from .views import test_api, login, me

urlpatterns = [
    path('test/', test_api),
    path('accounts/login/', login),
    path('accounts/me/', me),
]