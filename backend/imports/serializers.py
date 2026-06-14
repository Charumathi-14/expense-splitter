from rest_framework import serializers

from .models import ImportBatch, ImportIssue


class ImportIssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImportIssue
        fields = [
            'id',
            'row_number',
            'issue_type',
            'severity',
            'description',
            'action_taken',
            'status'
        ]


class ImportBatchSerializer(serializers.ModelSerializer):
    issues = ImportIssueSerializer(
        many=True,
        read_only=True,
        source='importissue_set'
    )

    class Meta:
        model = ImportBatch
        fields = [
            'id',
            'file_name',
            'imported_at',
            'issues'
        ]
