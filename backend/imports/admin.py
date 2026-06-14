from django.contrib import admin
from .models import ImportBatch, ImportIssue

admin.site.register(ImportBatch)
admin.site.register(ImportIssue)