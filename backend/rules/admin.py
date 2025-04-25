from django.contrib import admin
from .models import ProjectRule

@admin.register(ProjectRule)
class ProjectRuleAdmin(admin.ModelAdmin):
    list_display = ("project", "rule", "is_open", "votes_count")
    list_filter = ("is_open",)