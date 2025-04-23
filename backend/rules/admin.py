from django.contrib import admin
from .models import AnnotationRule, VotingConfig

class AnnotationRuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'created_by', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for uma criação, não uma edição
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class VotingConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'voting_type', 'min_votes', 'created_by')
    list_filter = ('project', 'voting_type')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Registrar os modelos
admin.site.register(AnnotationRule, AnnotationRuleAdmin)
admin.site.register(VotingConfig, VotingConfigAdmin)