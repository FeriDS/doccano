# profiles/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.contrib.auth.models import Permission
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PermissionSerializer
import logging

logger = logging.getLogger(__name__)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info("Fetching all user profiles")
        return UserProfile.objects.all()

    def list(self, request, *args, **kwargs):
        logger.info("List method called for user profiles")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Found {len(queryset)} profiles")
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()

    def get_queryset(self):
        return Permission.objects.all()

    def get(self, request):
        permissions = self.get_queryset()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
