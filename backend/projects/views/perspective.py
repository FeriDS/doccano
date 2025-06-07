from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Project, ProjectPerspective, PerspectiveField, UserPerspectiveAnswer
from ..permissions import IsProjectAdmin, IsAnnotatorAndHasValidPerspective
from ..serializers import (
    PerspectiveFieldSerializer,
    ProjectPerspectiveSerializer,
    UserPerspectiveAnswerSerializer,
)


class ProjectPerspectiveView(generics.RetrieveUpdateAPIView):
    serializer_class = ProjectPerspectiveSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]
    lookup_url_kwarg = 'project_id'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        perspective, created = ProjectPerspective.objects.get_or_create(project=project)
        return perspective


class PerspectiveFieldListView(generics.ListCreateAPIView):
    serializer_class = PerspectiveFieldSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        perspective = get_object_or_404(ProjectPerspective, project_id=project_id)
        return perspective.fields.all()

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        perspective = get_object_or_404(ProjectPerspective, project_id=project_id)
        field = serializer.save()
        perspective.fields.add(field)


class PerspectiveFieldDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PerspectiveFieldSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]
    lookup_url_kwarg = 'field_id'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        perspective = get_object_or_404(ProjectPerspective, project_id=project_id)
        return perspective.fields.all()


class UserPerspectiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        perspective = get_object_or_404(ProjectPerspective, project=project)
        answers = UserPerspectiveAnswer.objects.filter(
            user=request.user,
            project=project
        )
        
        # Format response to include all fields and their answers
        response_data = {
            'is_complete': True,
            'fields': []
        }
        
        for field in perspective.fields.all():
            answer = answers.filter(field=field).first()
            field_data = PerspectiveFieldSerializer(field).data
            field_data['answer'] = answer.value if answer else None
            response_data['fields'].append(field_data)
            
            # Check if required field is missing
            if field.required and not answer:
                response_data['is_complete'] = False
        
        return Response(response_data)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        perspective = get_object_or_404(ProjectPerspective, project=project)
        
        answers_data = request.data.get('answers', [])
        errors = []
        created_answers = []
        
        for answer_data in answers_data:
            field_id = answer_data.get('field')
            value = answer_data.get('value')
            
            if not field_id or value is None:
                errors.append(f"Missing field_id or value for answer")
                continue
                
            field = perspective.fields.filter(id=field_id).first()
            if not field:
                errors.append(f"Field {field_id} not found")
                continue
            
            serializer = UserPerspectiveAnswerSerializer(data={
                'user': request.user.id,
                'project': project.id,
                'field': field_id,
                'value': value
            })
            
            if serializer.is_valid():
                # Update or create the answer
                answer, created = UserPerspectiveAnswer.objects.update_or_create(
                    user=request.user,
                    project=project,
                    field=field,
                    defaults={'value': value}
                )
                created_answers.append(serializer.data)
            else:
                errors.append(serializer.errors)
        
        if errors and not created_answers:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'answers': created_answers,
            'errors': errors if errors else None
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)


class CheckPerspectiveCompletionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        perspective = get_object_or_404(ProjectPerspective, project=project)
        
        if not perspective.is_required:
            return Response({'is_complete': True})
        
        required_fields = perspective.fields.filter(required=True)
        answered_fields = UserPerspectiveAnswer.objects.filter(
            user=request.user,
            project=project,
            field__in=required_fields
        ).values_list('field_id', flat=True)
        
        is_complete = set(required_fields.values_list('id', flat=True)) <= set(answered_fields)
        
        return Response({
            'is_complete': is_complete,
            'missing_fields': list(required_fields.exclude(id__in=answered_fields).values('id', 'name'))
        }) 