from rest_framework import serializers

from .models import Expense
from .models import ExpenseParticipant


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = '__all__'


class ExpenseParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseParticipant
        fields = '__all__'