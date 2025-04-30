from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

from .models import ProjectRule, RuleVote
from .serializers import ProjectRuleSerializer, VoteInputSerializer, RuleCreateSerializer

class ProjectRuleCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RuleCreateSerializer

    def get_queryset(self):
        return self.queryset.filter(project_id=self.kwargs["project_id"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        serializer.save(project=project)

    def create(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        # Verifica se o usuário tem permissão para criar regras neste projeto
        if not request.user.is_staff and project.created_by != request.user:
            return Response(
                {"error": "Você não tem permissão para criar regras neste projeto."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Cria a regra básica
        rule_data = {"text": request.data.get("text")}
        rule_serializer = RuleSerializer(data=rule_data)
        rule_serializer.is_valid(raise_exception=True)
        rule = rule_serializer.save()

        # Cria a ligação com o projeto
        project_rule = ProjectRule.objects.create(
            project=project,
            rule=rule,
            is_open=True  # Por padrão, a votação começa aberta
        )

        serializer = self.get_serializer(project_rule)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProjectRuleAPIView(APIView):
    def get(self, request, project_id):  # 👈 Aceita GET
        rules = ProjectRule.objects.filter(project_id=project_id)
        serializer = ProjectRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):  # 👈 Aceita POST
        serializer = ProjectRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectRuleListView(generics.ListAPIView):
    serializer_class = ProjectRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        proj_id = self.kwargs["project_id"]
        return ProjectRule.objects.filter(project_id=proj_id)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class RuleVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id, rule_id):
        pr = get_object_or_404(
            ProjectRule,
            project_id=project_id,
            rule_id=rule_id
        )

        if not pr.is_open:
            return Response(
                {"error": "Votação encerrada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VoteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_val = serializer.validated_data["vote"]

        vote_obj, created = RuleVote.objects.update_or_create(
            project_rule=pr,
            user=request.user,
            defaults={"vote": vote_val}
        )

        yes = pr.votes.filter(vote=True).count()
        no = pr.votes.filter(vote=False).count()

        return Response({
            "message": "Voto registado." if created else "Voto atualizado.",
            "votes_yes": yes,
            "votes_no": no,
            "user_has_voted": True,
            "is_open": pr.is_open
        }, status=status.HTTP_201_CREATED)


class ProjectRuleUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def patch(self, request, project_id, rule_id):
        
        project_rule = get_object_or_404(
            ProjectRule,
            project_id=project_id,
            rule_id=rule_id
        )

        if "is_open" not in request.data:
            return Response(
                {"error": "Campo 'is_open' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Conversão segura para booleano
        is_open = request.data.get("is_open")
        if isinstance(is_open, str):
            is_open = is_open.lower() in ["true", "1", "yes"]
        elif isinstance(is_open, int):
            is_open = bool(is_open)

        project_rule.is_open = is_open
        project_rule.save()

        return Response({
            "message": "Estado de votação atualizado com sucesso.",
            "is_open": project_rule.is_open
        })
