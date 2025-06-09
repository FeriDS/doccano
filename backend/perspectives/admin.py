from django.contrib import admin
from .models import Perspective, PerspectiveField, ProjectPerspective, UserPerspectiveAnswer

@admin.register(PerspectiveField)
class PerspectiveFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'required', 'created_at')
    list_filter = ('field_type', 'required')
    search_fields = ('name', 'description')

@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('fields',)

@admin.register(ProjectPerspective)
class ProjectPerspectiveAdmin(admin.ModelAdmin):
    list_display = ('project', 'perspective', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__name', 'perspective__name')

@admin.register(UserPerspectiveAnswer)
class UserPerspectiveAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'project_perspective', 'is_complete', 'created_at')
    list_filter = ('is_complete', 'created_at')
    search_fields = ('user__username', 'project_perspective__project__name')
    readonly_fields = ('is_complete',)
