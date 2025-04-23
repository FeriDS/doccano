from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from examples.models import Example
from projects.models import Project
from labels.models import Category  # Corrigido: modelo certo para anotações
from .models import Discrepancy
from .serializers import DiscrepancySerializer
from .permissions import IsProjectAdmin


class ListExamplesWithAnnotationsView(APIView):
    permission_classes = [IsProjectAdmin]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Projeto não encontrado.'}, status=404)

        examples = Example.objects.filter(project=project)
        data = []

        for example in examples:
            annotations = Category.objects.filter(example=example)
            is_discrepancy_marked = Discrepancy.objects.filter(project=project, example=example).exists()
            data.append({
                'id': example.id,
                'text': example.text,
                'annotations': [
                    {
                        'id': annotation.id,
                        'user': annotation.user.username if annotation.user else 'Desconhecido',
                        'label': annotation.label.text if annotation.label else 'Sem rótulo'
                    }
                    for annotation in annotations
                ],
                'discrepancyMarked': is_discrepancy_marked 
            })

        return Response(data, status=status.HTTP_200_OK)


class DiscrepancyCreateView(APIView):
    permission_classes = [IsProjectAdmin]

    def post(self, request, project_id, example_id):
        project = get_object_or_404(Project, id=project_id)
        example = get_object_or_404(Example, id=example_id, project=project)

        # Verifica se há pelo menos 2 anotações diferentes
        annotation_count = Category.objects.filter(example=example).values('user').distinct().count()
        if annotation_count < 2:
            return Response({'error': 'É necessário pelo menos duas anotações para sinalizar discrepância.'}, status=400)
        
        if Discrepancy.objects.filter(project=project, example=example).exists():
            return Response({'error': 'Discrepância já sinalizada para este exemplo.'}, status=400)

        discrepancy = Discrepancy.objects.create(
            project=project,
            example=example,
            created_by=request.user
        )
        serializer = DiscrepancySerializer(discrepancy)
        return Response(serializer.data, status=201)
