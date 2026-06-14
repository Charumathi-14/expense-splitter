from django.db import models
from groups.models import Group
from accounts.models import User


class Expense(models.Model):

    SPLIT_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
        ('weight', 'Weight')
    ]

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default='INR'
    )

    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses_paid"
    )

    split_type = models.CharField(
        max_length=20,
        choices=SPLIT_CHOICES
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
class ExpenseParticipant(models.Model):

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    share_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    weight = models.IntegerField(
        default=1
    )