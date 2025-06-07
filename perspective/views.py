from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from projects.models import Project
from projects.serializers import ProjectSerializer
from .models import Perspective, PerspectiveField
from .serializers import PerspectiveSerializer

class IsProjectAdmin(permissions.BasePermission):
    """Custom permission to only allow project admins to edit perspectives."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        project_id = view.kwargs.get('project_id')
        if not project_id:
            return False
        project = get_object_or_404(Project, id=project_id)
        return request.user.is_superuser or project.created_by == request.user

class ProjectsWithoutPerspectives(generics.ListAPIView):
    """List all projects that don't have perspectives configured."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        return Project.objects.exclude(
            id__in=Perspective.objects.values_list('project_id', flat=True)
        )

class PerspectiveList(generics.ListCreateAPIView):
    """List all perspectives or create a new one."""
    serializer_class = PerspectiveSerializer
    permission_classes = [IsProjectAdmin]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Perspective.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project)

class PerspectiveDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a perspective."""
    serializer_class = PerspectiveSerializer
    permission_classes = [IsProjectAdmin]
    lookup_url_kwarg = 'perspective_id'

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Perspective.objects.filter(project_id=project_id) 