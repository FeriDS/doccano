from rest_framework.permissions import BasePermission
from django.conf import settings 
from projects.models import Member

class IsProjectAdmin(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')
        if not project_id:
            return False
        return Member.objects.has_role(project_id, request.user, settings.ROLE_PROJECT_ADMIN)

