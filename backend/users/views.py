from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction, connection
import logging

from .serializers import UserSerializer
from projects.permissions import IsProjectAdmin

logger = logging.getLogger(__name__)


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class Users(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("username",)


class UserCreation(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        return user
    
class UserRetrieve(APIView):  # New view to get user id by username
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get(self, request, username, *args, **kwargs):
        try:
            user = User.objects.get(username=username)
            return Response({"id": user.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class UserDelete(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superusers can delete users."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = kwargs.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Attempting to delete user {user.id} ({user.username})")

        try:
            with transaction.atomic():
                # Remover project memberships, comentários, exemplos, etc.
                from projects.models import Project, Member
                Member.objects.filter(user=user).delete()
                Project.objects.filter(created_by=user).update(created_by=None)

                from examples.models import Example, Comment
                Example.objects.filter(annotations_approved_by=user).update(annotations_approved_by=None)
                Comment.objects.filter(user=user).delete()

                # Limpar votos das regras usando SQL direto
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM rules_rulevote WHERE user_id = %s", [user.id])
                except Exception as e:
                    logger.warning(f"Could not clean up rule votes: {e}")

                # Finalmente, apagar o utilizador
                user.delete()

            logger.info(f"Successfully deleted user {user.id}")
            return Response(
                {"message": "User deleted successfully."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during user deletion: {e}", exc_info=True)
            return Response(
                {"error": "Failed to delete user. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
