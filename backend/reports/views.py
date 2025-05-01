from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from .models import AnnotationReport
from .serializer import AnnotationReportSerializer
from labels.models import Span
from django.utils.timezone import make_aware
from datetime import datetime

class AnnotationReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({"error": "Project ID obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        reports = AnnotationReport.objects.filter(project_id=project_id).order_by('-created_at')
        serializer = AnnotationReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({"error": "Project ID obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        report = AnnotationReport.objects.create(
            project_id=project_id,
            created_by=request.user,
            filters={}
        )

        # Devolve apenas id e created_at diretamente para simplificar a resposta
        return Response({
            'id': report.id,
            'created_at': report.created_at
        }, status=status.HTTP_201_CREATED)

class AnnotationReportDataView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        report = get_object_or_404(AnnotationReport, pk=pk)
        filters = report.filters
        queryset = Span.objects.filter(example__project_id=report.project_id)

        if filters.get('annotator_id'):
            queryset = queryset.filter(user_id=filters['annotator_id'])

        if filters.get('start_date'):
            start = make_aware(datetime.strptime(filters['start_date'], '%Y-%m-%d'))
            queryset = queryset.filter(created_at__gte=start)

        if filters.get('end_date'):
            end = make_aware(datetime.strptime(filters['end_date'], '%Y-%m-%d'))
            queryset = queryset.filter(created_at__lte=end)

        data = [
            {
                'id': span.id,
                'text': span.example.text[
                    span.start_offset:span.end_offset
                ],
                'user': span.user.username,
                'created_at': span.created_at,
                'project': span.example.project.name,
                'perspective': None
            }
            for span in queryset.select_related('user', 'example__project')
        ]

        return Response({
            'report_id': report.id,
            'created_at': report.created_at,
            'filters': filters,
            'results': data
        })
