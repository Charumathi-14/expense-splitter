from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

from expenses.models import Expense, ExpenseParticipant
from settlements.models import Settlement


def _to_decimal(value):
    if isinstance(value, Decimal):
        return value
    return Decimal(value)


def convert_currency(amount, currency):
    rates = getattr(settings, 'CURRENCY_RATES', {'INR': Decimal('1'), 'USD': Decimal('82.00')})
    rate = rates.get(currency.upper(), None)
    if rate is None:
        return _to_decimal(amount)
    return (_to_decimal(amount) * _to_decimal(rate)).quantize(Decimal('0.01'))


def calculate_group_balance(group_id):
    balances = {}

    expenses = Expense.objects.filter(group_id=group_id)

    for expense in expenses:
        total = convert_currency(expense.amount, expense.currency)
        participants = ExpenseParticipant.objects.filter(expense=expense)
        participant_shares = []

        if expense.split_type == 'equal' or not participants.exists():
            count = participants.count() or 1
            share = (total / count).quantize(Decimal('0.01'))
            for participant in participants:
                participant_shares.append((participant.user.id, share))
        elif expense.split_type == 'exact':
            for participant in participants:
                participant_shares.append((participant.user.id, convert_currency(participant.share_amount, expense.currency)))
        elif expense.split_type == 'percentage':
            for participant in participants:
                participant_shares.append((
                    participant.user.id,
                    (total * Decimal(participant.percentage) / Decimal('100')).quantize(Decimal('0.01'))
                ))
        elif expense.split_type == 'weight':
            total_weight = sum(participant.weight for participant in participants)
            if total_weight == 0:
                equal_share = (total / participants.count()).quantize(Decimal('0.01'))
                for participant in participants:
                    participant_shares.append((participant.user.id, equal_share))
            else:
                for participant in participants:
                    participant_shares.append((
                        participant.user.id,
                        (total * Decimal(participant.weight) / Decimal(total_weight)).quantize(Decimal('0.01'))
                    ))
        else:
            count = participants.count() or 1
            share = (total / count).quantize(Decimal('0.01'))
            for participant in participants:
                participant_shares.append((participant.user.id, share))

        payer_id = expense.paid_by.id
        balances[payer_id] = balances.get(payer_id, Decimal('0.00')) + total

        for user_id, share in participant_shares:
            balances[user_id] = balances.get(user_id, Decimal('0.00')) - share

    settlements = Settlement.objects.filter(group_id=group_id)
    for settlement in settlements:
        amount = convert_currency(settlement.amount, settlement.currency)
        payer_id = settlement.payer.id
        receiver_id = settlement.receiver.id

        balances[payer_id] = balances.get(payer_id, Decimal('0.00')) - amount
        balances[receiver_id] = balances.get(receiver_id, Decimal('0.00')) + amount

    return {user_id: balance.quantize(Decimal('0.01')) for user_id, balance in balances.items()}


def build_settlement_suggestions(balances):
    debtors = [
        {'user_id': user_id, 'balance': -amount}
        for user_id, amount in balances.items() if amount < 0
    ]
    creditors = [
        {'user_id': user_id, 'balance': amount}
        for user_id, amount in balances.items() if amount > 0
    ]

    debtors.sort(key=lambda item: item['balance'], reverse=True)
    creditors.sort(key=lambda item: item['balance'], reverse=True)

    suggestions = []
    d_index = 0
    c_index = 0

    while d_index < len(debtors) and c_index < len(creditors):
        debtor = debtors[d_index]
        creditor = creditors[c_index]
        amount = min(debtor['balance'], creditor['balance'])

        suggestions.append({
            'from_user_id': debtor['user_id'],
            'to_user_id': creditor['user_id'],
            'amount': str(amount.quantize(Decimal('0.01')))
        })

        debtor['balance'] -= amount
        creditor['balance'] -= amount

        if debtor['balance'] <= 0:
            d_index += 1
        if creditor['balance'] <= 0:
            c_index += 1

    return suggestions
