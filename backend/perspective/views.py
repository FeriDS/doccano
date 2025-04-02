# from rest_framework import generics, permissions
# from .models import Perspective
# from .serializers import PerspectiveSerializer

# class PerspectiveList(generics.ListAPIView):
#     """
#     Endpoint para listar todas as perspectivas
#     """
#     queryset = Perspective.objects.all().order_by('-created_at')
#     serializer_class = PerspectiveSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Perspective.objects.all().prefetch_related('projects')  # Carrega relações

# class PerspectiveDetail(generics.RetrieveAPIView):
#     """
#     Endpoint para detalhes de uma perspectiva
#     """
#     queryset = Perspective.objects.all()
#     serializer_class = PerspectiveSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'id'

from rest_framework import generics
from django.db.models import Prefetch
from .models import Perspective
from .serializers import PerspectiveSerializer

class PerspectiveList(generics.ListAPIView):
    serializer_class = PerspectiveSerializer
    
    def get_queryset(self):
        return Perspective.objects.prefetch_related(
            Prefetch('projects', queryset=Project.objects.only('id', 'name'))
        ).all()