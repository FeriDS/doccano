from rest_framework import serializers
from .models import Rule, ProjectRule

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "text"]

class ProjectRuleSerializer(serializers.ModelSerializer):
    rule = RuleSerializer(read_only=True)
    votes_yes = serializers.SerializerMethodField()
    votes_no = serializers.SerializerMethodField()
    votes_count = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    vote = serializers.SerializerMethodField()  # <- Adicionado aqui!
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProjectRule
        fields = [
            "id", "project", "rule",
            "is_open",
            "votes_yes", "votes_no", "votes_count",
            "user_has_voted", "vote"  # <- Também aqui!
        ]
        read_only_fields = [
            "is_open", "votes_yes", "votes_no",
            "votes_count", "user_has_voted", "vote"
        ]

    def get_votes_yes(self, obj):
        return obj.votes.filter(vote=True).count()

    def get_votes_no(self, obj):
        return obj.votes.filter(vote=False).count()

    def get_votes_count(self, obj):
        return obj.votes.count()

    def get_user_has_voted(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.votes.filter(user=request.user).exists()
        return False

    def get_vote(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            vote_obj = obj.votes.filter(user=request.user).first()
            if vote_obj:
                return vote_obj.vote  # True ou False
        return None  # Não votou ainda

class VoteInputSerializer(serializers.Serializer):
    vote = serializers.BooleanField()

class CreateProjectRuleSerializer(serializers.ModelSerializer):
    text = serializers.CharField(write_only=True)

    class Meta:
        model = ProjectRule
        fields = ['id', 'project', 'is_open', 'text']
        read_only_fields = ['id', 'project', 'is_open']

    def create(self, validated_data):
        text = validated_data.pop('text')
        project = self.context['project']
        rule = Rule.objects.create(text=text)
        project_rule = ProjectRule.objects.create(project=project, rule=rule)
        return project_rule
