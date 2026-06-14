from rest_framework import viewsets

from .models import Expense
from .models import ExpenseParticipant

from .serializers import ExpenseSerializer
from .serializers import ExpenseParticipantSerializer


class ExpenseViewSet(viewsets.ModelViewSet):

    queryset = Expense.objects.all()

    serializer_class = ExpenseSerializer


class ExpenseParticipantViewSet(viewsets.ModelViewSet):

    queryset = ExpenseParticipant.objects.all()

    serializer_class = ExpenseParticipantSerializer