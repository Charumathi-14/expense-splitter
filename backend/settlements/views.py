from rest_framework import viewsets

from .models import Settlement
from .serializers import SettlementSerializer


class SettlementViewSet(viewsets.ModelViewSet):

    queryset = Settlement.objects.all()

    serializer_class = SettlementSerializer