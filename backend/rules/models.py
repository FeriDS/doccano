from django.db import models
from django.conf import settings
from projects.models import Project

class Rule(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:50] + ("..." if len(self.text) > 50 else "")

class ProjectRule(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_rules"
    )
    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        related_name="project_links"
    )
    is_open = models.BooleanField(
        default=True,
        help_text="Se True, permite votar nesta regra"
    )

    class Meta:
        unique_together = ("project", "rule")

    def __str__(self):
        return f"{self.project.name} – {self.rule.text[:30]}"

    def votes_count(self):
        yes = self.votes.filter(vote=True).count()
        no  = self.votes.filter(vote=False).count()
        return yes, no
    
    def is_voting_closed(self):
        return not self.is_open

class RuleVote(models.Model):
    project_rule = models.ForeignKey(
        ProjectRule,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    vote = models.BooleanField()        # True=sim, False=não
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project_rule", "user")

    def __str__(self):
        return f"{self.user.username} votou {'sim' if self.vote else 'no'}"