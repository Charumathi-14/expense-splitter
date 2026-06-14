import io

from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ImportBatch, ImportIssue
from .serializers import ImportBatchSerializer, ImportIssueSerializer
from .services.csv_importer import CSVImporter


class ImportBatchViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ImportBatch.objects.all().order_by('-imported_at')
    serializer_class = ImportBatchSerializer


class ImportIssueViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ImportIssue.objects.all().order_by('-batch', 'row_number')
    serializer_class = ImportIssueSerializer


class ImportUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')

        if file_obj is None:
            return Response(
                {'detail': 'Missing uploaded file under key "file".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        batch = ImportBatch.objects.create(file_name=file_obj.name)
        importer = CSVImporter()
        report = importer.process(file_obj, batch=batch)

        serializer = ImportBatchSerializer(batch)
        return Response({
            'batch': serializer.data,
            'summary': report
        }, status=status.HTTP_201_CREATED)
