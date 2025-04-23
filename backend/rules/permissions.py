from rest_framework.permissions import BasePermission
from projects.models import Project

class IsProjectManager(BasePermission):
    """Permissão que permite apenas gestores do projeto"""
    
    def has_permission(self, request, view):
        # Verifica se o usuário é gestor do projeto
        project_id = request.query_params.get('project') or request.data.get('project')
        if not project_id:
            return False
            
        try:
            project = Project.objects.get(id=project_id)
            return project.can_manage(request.user)
        except Project.DoesNotExist:
            return False