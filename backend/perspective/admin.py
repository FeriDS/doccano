from django.contrib import admin
from .models import Perspective

class PerspectiveProjectInline(admin.TabularInline):
    model = Perspective.projects.through
    extra = 1

@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_list')  # Mostra projetos associados
    
    def project_list(self, obj):
        return ", ".join([p.name for p in obj.projects.all()])