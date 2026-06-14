from django.contrib import admin
from .models import Expense, ExpenseParticipant

admin.site.register(Expense)
admin.site.register(ExpenseParticipant)