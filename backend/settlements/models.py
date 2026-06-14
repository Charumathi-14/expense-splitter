from django.db import models
from groups.models import Group
from accounts.models import User


class Settlement(models.Model):

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )

    payer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments_made"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments_received"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default='INR'
    )

    settlement_date = models.DateField()

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )