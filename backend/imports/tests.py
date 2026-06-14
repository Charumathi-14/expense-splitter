from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ImportBatch, ImportIssue
from .services.csv_importer import CSVImporter
from accounts.models import User
from groups.models import Group


class CSVImporterTests(TestCase):

    def test_basic_csv_import_creates_expense(self):
        csv_content = (
            'group,date,amount,paid_by,participants,description\n'
            'Flatmates,2024-05-01,1000,Aisha,Aisha;Rohan;Priya;Meera,Groceries\n'
        )
        file_obj = SimpleUploadedFile(
            'expenses_export.csv',
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        batch = ImportBatch.objects.create(file_name='expenses_export.csv')
        report = CSVImporter().process(file_obj, batch=batch)

        self.assertEqual(report['created']['expenses'], 1)
        self.assertEqual(report['created']['skipped'], 0)
        self.assertEqual(report['created']['settlements'], 0)
        self.assertEqual(ImportIssue.objects.filter(severity='error').count(), 0)
        self.assertTrue(User.objects.filter(name='Aisha').exists())
        self.assertTrue(Group.objects.filter(name='Flatmates').exists())
