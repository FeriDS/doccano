# profiles/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.contrib.auth.models import Permission
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PermissionSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.all()

    def perform_create(self, serializer):
        serializer.save()

class PermissionListView(APIView):
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
