from rest_framework import generics, permissions
from .models import PerspectiveField, UserPerspectiveAnswer
from .serializers import PerspectiveFieldSerializer, UserPerspectiveAnswerSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from projects.models import Project

class GetProjectPerspectiveFields(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)

            if not hasattr(project, 'project_perspective'):
                return Response({'error': 'Este projeto não tem uma perspetiva associada.'}, status=400)

            perspective = project.project_perspective.perspective
            fields = perspective.fields.all()
            serializer = PerspectiveFieldSerializer(fields, many=True)
            return Response(serializer.data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)


class SubmitUserPerspectiveAnswers(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        user = request.user
        project = get_object_or_404(Project, id=project_id)

        # ✅ Verifica se o user já respondeu a essa perspetiva
        if UserPerspectiveAnswer.objects.filter(user=user, project=project).exists():
            return Response(
                {"error": "Já preencheu a perspetiva deste projeto."},
                status=400
            )
        data = request.data  # Espera uma lista de dicts: [{'field_id': 1, 'value': ...}, ...]

        for item in data:
            field_id = item.get('field_id')
            field = get_object_or_404(PerspectiveField, id=field_id)
            obj = UserPerspectiveAnswer(
                user=user,
                project=project,
                field=field
            )
            # guarda o valor dependendo do tipo
            if field.field_type == 'int':
                obj.value_int = item.get('value')
            elif field.field_type == 'bool':
                obj.value_bool = item.get('value')
            else:
                obj.value_string = item.get('value')

            obj.save()

        return Response({"message": "Respostas guardadas com sucesso."})

