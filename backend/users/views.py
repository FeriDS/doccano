from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
#adding user delete (luz)
#from django.http import JsonResponse
#from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required, user_passes_test
#end user delete (luz)
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from projects.permissions import IsProjectAdmin


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
    
#delete user change (luz)
#def is_admin(user):
#    return user.is_superuser

#@login_required
#@user_passes_test(is_admin)
#def delete_user(request, user_id):
#    try:
#        user = User.objects.get(id=user_id)
#        user.delete()
#        return JsonResponse({"message": "Usuário deletado com sucesso."}, status=200)
#    except User.DoesNotExist:
#        return JsonResponse({"error": "Usuário não encontrado."}, status=404)
#end delete user change (luz)