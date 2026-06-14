from django.db import models

class ImportBatch(models.Model):

    file_name = models.CharField(
        max_length=255
    )

    imported_at = models.DateTimeField(
        auto_now_add=True
    )


class ImportIssue(models.Model):

    batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE
    )

    row_number = models.IntegerField()

    issue_type = models.CharField(
        max_length=100
    )

    severity = models.CharField(
        max_length=50
    )

    description = models.TextField()

    action_taken = models.TextField()

    status = models.CharField(
        max_length=50,
        default="pending"
    )