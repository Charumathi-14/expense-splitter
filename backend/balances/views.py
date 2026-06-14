from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.calculator import calculate_group_balance, build_settlement_suggestions
from groups.models import Group
from accounts.models import User


class GroupBalanceView(APIView):

    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {'detail': 'Group not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        balances = calculate_group_balance(group_id)
        suggestions = build_settlement_suggestions(balances)

        return Response({
            'group': group.name,
            'balances': [
                {
                    'user_id': user_id,
                    'user_name': User.objects.filter(id=user_id).first().name if User.objects.filter(id=user_id).exists() else None,
                    'balance': str(amount)
                }
                for user_id, amount in balances.items()
            ],
            'recommended_settlements': suggestions
        })
