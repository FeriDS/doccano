from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404
from django.db import transaction
from projects.permissions import IsProjectMember
from .models import Perspective, PerspectiveField, ProjectPerspective, UserPerspectiveAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


from .serializers import (
    PerspectiveSerializer, 
    PerspectiveFieldSerializer,
    ProjectPerspectiveSerializer,
    UserPerspectiveAnswerSerializer
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_perspective_answer(request, project_id):
    project_perspective = get_object_or_404(
        ProjectPerspective,
        project_id=project_id
    )

    instance, _created = UserPerspectiveAnswer.objects.get_or_create(
        project_perspective=project_perspective,
        user=request.user
    )

    serializer = UserPerspectiveAnswerSerializer(instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_perspective_answers(request, project_id):
    answers = UserPerspectiveAnswer.objects.filter(
        project_perspective__project_id=project_id,
        user=request.user
    )
    serializer = UserPerspectiveAnswerSerializer(answers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_perspective(request, project_id):
    perspective = get_object_or_404(ProjectPerspective, project_id=project_id)
    serializer = ProjectPerspectiveSerializer(perspective)
    return Response(serializer.data)

class PerspectiveFieldViewSet(viewsets.ModelViewSet):
    serializer_class = PerspectiveFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PerspectiveField.objects.all()
    renderer_classes = [JSONRenderer]

class PerspectiveViewSet(viewsets.ModelViewSet):
    serializer_class = PerspectiveSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Perspective.objects.all()
    renderer_classes = [JSONRenderer]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_field(self, request, pk=None):
        perspective = self.get_object()
        field_serializer = PerspectiveFieldSerializer(data=request.data)
        
        if field_serializer.is_valid():
            field = field_serializer.save()
            perspective.fields.add(field)
            return Response(field_serializer.data, status=status.HTTP_201_CREATED)
        return Response(field_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectPerspectiveViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectPerspectiveSerializer
    permission_classes = [permissions.IsAuthenticated & IsProjectMember]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return ProjectPerspective.objects.filter(project_id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_values(self, request, pk=None):
        project_perspective = self.get_object()
        
        # Update field values
        field_values = request.data.get('field_values', {})
        if not field_values:
            return Response(
                {'error': 'field_values is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate field values
        serializer = self.get_serializer(project_perspective, data={'field_values': field_values}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def check_completion(self, request, pk=None):
        project_perspective = self.get_object()
        return Response({
            'is_complete': project_perspective.is_complete,
            'missing_fields': [
                field.name for field in project_perspective.perspective.fields.filter(required=True)
                if field.name not in project_perspective.field_values
            ]
        })

class UserPerspectiveAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = UserPerspectiveAnswerSerializer
    permission_classes = [permissions.IsAuthenticated & IsProjectMember]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return UserPerspectiveAnswer.objects.filter(
            project_perspective__project_id=self.kwargs['project_id']
        )

    def perform_create(self, serializer):
        project_perspective = get_object_or_404(
            ProjectPerspective,
            project_id=self.kwargs['project_id']
        )
        serializer.save(
            project_perspective=project_perspective,
            user=self.request.user
        )

    @action(detail=True, methods=['patch'])
    def update_values(self, request, pk=None):
        user_answer = self.get_object()
        
        # Update field values
        field_values = request.data.get('field_values', {})
        if not field_values:
            return Response(
                {'error': 'field_values is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate field values
        serializer = self.get_serializer(user_answer, data={'field_values': field_values}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def check_completion(self, request, pk=None):
        user_answer = self.get_object()
        return Response({
            'is_complete': user_answer.is_complete,
            'missing_fields': [
                field.name for field in user_answer.project_perspective.perspective.fields.filter(required=True)
                if field.name not in user_answer.field_values
            ]
        })

    @action(detail=False, methods=['patch'], url_path='update', url_name='update')
    def update_current_user_answer(self, request, project_id=None):
        try:
            instance = UserPerspectiveAnswer.objects.get(
                project_perspective__project_id=project_id,
                user=request.user
            )
        except UserPerspectiveAnswer.DoesNotExist:
            return Response({'error': 'User answer not found'}, status=404)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
