# backend/reports/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate

from labels.models import Span, Category, TextLabel
from projects.models import Project
from backend.rules.models import Rule

from .models import HistoricalReport
from .serializer import HistoricalReportSerializer

import csv
import io
from collections import defaultdict
from datetime import datetime


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

        # Filtros base
        filters = {'example__project': project}
        if user_id:
            filters['user_id'] = user_id
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date

        # Obter anotações de todos os tipos
        spans = Span.objects.filter(**filters)
        categories = Category.objects.filter(**filters)
        text_labels = TextLabel.objects.filter(**filters)

        # Calcular estatísticas por utilizador
        user_annotations = defaultdict(int)
        for model in [spans, categories, text_labels]:
            for annotation in model:
                user_annotations[annotation.user_id] += 1

        # Calcular estatísticas por data
        date_annotations = defaultdict(int)
        for model in [spans, categories, text_labels]:
            for annotation in model:
                date = annotation.created_at.date()
                date_annotations[str(date)] += 1

        # Calcular estatísticas por tipo
        type_annotations = {
            'span': spans.count(),
            'category': categories.count(),
            'text': text_labels.count()
        }

        # Calcular totais e médias
        total_annotations = sum(type_annotations.values())
        total_users = len(user_annotations)
        rules_count = Rule.objects.filter(project=project).count()
        
        avg_annotations_per_user = total_annotations / total_users if total_users > 0 else 0
        avg_annotations_per_day = total_annotations / len(date_annotations) if date_annotations else 0

        # Criar relatório
        report_obj = HistoricalReport.objects.create(
            project=project,
            created_by=request.user,
            user_filter_id=user_id if user_id else None,
            start_date=start_date or None,
            end_date=end_date or None,
            total_annotations=total_annotations,
            total_users=total_users,
            rules_count=rules_count,
            annotations_per_user=dict(user_annotations),
            avg_annotations_per_user=avg_annotations_per_user,
            annotations_per_day=dict(date_annotations),
            avg_annotations_per_day=avg_annotations_per_day,
            annotations_by_type=type_annotations
        )

        data = {
            "report_id": report_obj.id,
            "total_annotations": total_annotations,
            "total_users": total_users,
            "rules_count": rules_count,
            "annotations_per_user": dict(user_annotations),
            "avg_annotations_per_user": avg_annotations_per_user,
            "annotations_per_day": dict(date_annotations),
            "avg_annotations_per_day": avg_annotations_per_day,
            "annotations_by_type": type_annotations
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
        
        # Escrever cabeçalho
        writer.writerow([
            "Total de Anotações", 
            "Total de Utilizadores", 
            "Regras Definidas",
            "Média de Anotações por Utilizador",
            "Média de Anotações por Dia"
        ])
        
        # Escrever dados gerais
        writer.writerow([
            data["total_annotations"],
            data["total_users"],
            data["rules_count"],
            data["avg_annotations_per_user"],
            data["avg_annotations_per_day"]
        ])
        
        # Escrever dados por utilizador
        writer.writerow([])
        writer.writerow(["Anotações por Utilizador"])
        for user_id, count in data["annotations_per_user"].items():
            writer.writerow([f"Utilizador {user_id}", count])
            
        # Escrever dados por dia
        writer.writerow([])
        writer.writerow(["Anotações por Dia"])
        for date, count in data["annotations_per_day"].items():
            writer.writerow([date, count])
            
        # Escrever dados por tipo
        writer.writerow([])
        writer.writerow(["Anotações por Tipo"])
        for type_name, count in data["annotations_by_type"].items():
            writer.writerow([type_name, count])

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
        y -= 20
        p.drawString(100, y, f"Média de Anotações por Utilizador: {data['avg_annotations_per_user']:.2f}")
        y -= 20
        p.drawString(100, y, f"Média de Anotações por Dia: {data['avg_annotations_per_day']:.2f}")

        # Nova página para detalhes
        p.showPage()
        p.setFont("Helvetica", 12)
        y = 800

        # Anotações por utilizador
        p.drawString(100, y, "Anotações por Utilizador:")
        y -= 20
        for user_id, count in data["annotations_per_user"].items():
            p.drawString(120, y, f"Utilizador {user_id}: {count}")
            y -= 20

        # Anotações por dia
        y -= 20
        p.drawString(100, y, "Anotações por Dia:")
        y -= 20
        for date, count in data["annotations_per_day"].items():
            p.drawString(120, y, f"{date}: {count}")
            y -= 20

        # Anotações por tipo
        y -= 20
        p.drawString(100, y, "Anotações por Tipo:")
        y -= 20
        for type_name, count in data["annotations_by_type"].items():
            p.drawString(120, y, f"{type_name}: {count}")
            y -= 20

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
        return HistoricalReport.objects.filter(project_id=project_id).order_by("-created_at")


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
