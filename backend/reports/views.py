# backend/reports/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Count

from labels.models import Span
from projects.models import Project
from backend.rules.models import Rule

from .models import HistoricalReport
from .serializer import HistoricalReportSerializer

import csv
import io


User = get_user_model()


class HistoricalAnnotationReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        print(f"🔍 Pedido GET para exportação do projeto {project_id}")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"erro": f"Projeto {project_id} não encontrado."}, status=404)

        user_id = request.GET.get('user_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        export_format = request.GET.get('format', '').strip()

        spans = Span.objects.filter(example__project=project)

        if user_id:
            spans = spans.filter(user_id=user_id)
        if start_date:
            spans = spans.filter(created_at__gte=start_date)
        if end_date:
            spans = spans.filter(created_at__lte=end_date)

        total_annotations = spans.count()
        total_users = User.objects.filter(span__example__project=project).distinct().count()
        rules_count = Rule.objects.filter(project_links=project).count()

        report_obj = HistoricalReport.objects.create(
            project=project,
            created_by=request.user,
            user_filter_id=user_id if user_id else None,
            start_date=start_date or None,
            end_date=end_date or None,
            total_annotations=total_annotations,
            total_users=total_users,
            rules_count=rules_count
        )

        data = {
            "report_id": report_obj.id,
            "total_annotations": total_annotations,
            "total_users": total_users,
            "rules_count": rules_count,
        }

        print("📦 Dados a exportar:", data)

        if export_format == "csv":
            return self.export_csv(data)
        elif export_format == "pdf":
            return self.export_pdf(data)

        return Response(data)

    def export_csv(self, data):
        print("DATA A EXPORTAR:", data)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Total de Anotações", "Total de Utilizadores", "Regras Definidas"])
        writer.writerow([data["total_annotations"], data["total_users"], data["rules_count"]])

        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=relatorio.csv'
        return response

    def export_pdf(self, data):
        from reportlab.pdfgen import canvas
        import io

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)

        y = 800
        p.drawString(100, y, "📄 Relatório de Anotações")
        y -= 30
        p.drawString(100, y, f"Total de Anotações: {data['total_annotations']}")
        y -= 20
        p.drawString(100, y, f"Total de Utilizadores: {data['total_users']}")
        y -= 20
        p.drawString(100, y, f"Regras Definidas: {data['rules_count']}")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=relatorio.pdf'
        return response


class HistoricalReportListView(ListAPIView):
    serializer_class = HistoricalReportSerializer
    renderer_classes = [JSONRenderer]  # força resposta JSON

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return HistoricalReport.objects.filter(project_links_id=project_id).order_by("-created_at")


# Testes e debug

def teste_de_rota(request, project_id):
    return HttpResponse(f"FUNCIONA: project_id={project_id}", content_type="text/plain")


def pdf_teste(request):
    from reportlab.pdfgen import canvas
    import io

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "TESTE PDF GERADO COM SUCESSO")
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
