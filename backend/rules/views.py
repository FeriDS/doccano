from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
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

        if RuleVote.objects.filter(
            project_rule=pr,
            user=request.user
        ).exists():
            return Response(
                {"error": "Você já votou nesta regra."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VoteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_val = serializer.validated_data["vote"]

        RuleVote.objects.create(
            project_rule=pr,
            user=request.user,
            vote=vote_val
        )

        yes = pr.votes.filter(vote=True).count()
        no  = pr.votes.filter(vote=False).count()

        return Response({
            "message": "Voto registado.",
            "votes_yes": yes,
            "votes_no": no,
            "user_has_voted": True,
            "is_open": pr.is_open
        }, status=status.HTTP_201_CREATED)
