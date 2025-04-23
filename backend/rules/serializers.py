from rest_framework import serializers
from .models import Rule, ProjectRule

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "text"]

class ProjectRuleSerializer(serializers.ModelSerializer):
    rule = RuleSerializer(read_only=True)
    votes_yes = serializers.SerializerMethodField()
    votes_no  = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProjectRule
        fields = [
            "id", "rule", "votes_yes", "votes_no",
            "user_has_voted", "is_open",
        ]

    def get_votes_yes(self, obj):
        return obj.votes.filter(vote=True).count()

    def get_votes_no(self, obj):
        return obj.votes.filter(vote=False).count()

    def get_user_has_voted(self, obj):
        req = self.context.get("request")
        return bool(req and req.user.is_authenticated and
                    obj.votes.filter(user=req.user).exists())

class VoteInputSerializer(serializers.Serializer):
    vote = serializers.BooleanField()
