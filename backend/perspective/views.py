from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from .models import Perspective
from .serializers import PerspectiveSerializer
from .permissions import IsProjectAdmin
from projects.models import Project
from projects.serializers import ProjectSerializer

class ProjectsWithoutPerspectives(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.annotate(num_perspectives=Count('perspectives')).filter(num_perspectives=0)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

class PerspectiveList(generics.ListCreateAPIView):
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Perspective.objects.filter(project=self.kwargs["project_id"])

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_id"])
        serializer.save(project=project)



class PerspectiveDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Perspective.objects.all()
    serializer_class = PerspectiveSerializer
    lookup_url_kwarg = "perspective_id"
    permission_classes = [IsAuthenticated & IsProjectAdmin]
