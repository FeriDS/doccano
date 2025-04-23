from rest_framework import viewsets
from .models import AnnotationRule, VotingConfig
from .serializers import AnnotationRuleSerializer, VotingConfigSerializer
from .permissions import IsProjectManager

class AnnotationRuleViewSet(viewsets.ModelViewSet):
    queryset = AnnotationRule.objects.all()
    serializer_class = AnnotationRuleSerializer
    permission_classes = [IsProjectManager]  # Apenas gestores

    def get_queryset(self):
        # Filtra regras por projeto
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class VotingConfigViewSet(viewsets.ModelViewSet):
    queryset = VotingConfig.objects.all()
    serializer_class = VotingConfigSerializer
    permission_classes = [IsProjectManager]  # Apenas gestores

    def get_queryset(self):
        # Filtra configurações por projeto
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)