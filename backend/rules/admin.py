from django.contrib import admin
from .models import Rule, ProjectRule, RuleVote


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("id", "text")
    search_fields = ("text",)


class RuleVoteInline(admin.TabularInline):
    model = RuleVote
    extra = 0
    readonly_fields = ("user", "vote", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # Impede adicionar votos manualmente pelo admin


@admin.register(ProjectRule)
class ProjectRuleAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "rule", "is_open", "votes_yes", "votes_no")
    list_filter = ("is_open", "project")
    search_fields = ("rule__text", "project__name")
    inlines = [RuleVoteInline]

    def votes_yes(self, obj):
        return obj.votes.filter(vote=True).count()

    def votes_no(self, obj):
        return obj.votes.filter(vote=False).count()

    votes_yes.short_description = "Votos Sim"
    votes_no.short_description = "Votos Não"
