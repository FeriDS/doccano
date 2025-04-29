from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

from .models import ProjectRule, RuleVote
from .serializers import ProjectRuleSerializer, VoteInputSerializer


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

class ProjectRuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return ProjectRule.objects.filter(project_id=self.kwargs["project_id"])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProjectRuleSerializer
        return ProjectRuleSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        if self.request.method == 'POST':
            from projects.models import Project
            ctx["project"] = get_object_or_404(Project, id=self.kwargs["project_id"])
        return ctx

    def perform_create(self, serializer):
        serializer.save()

