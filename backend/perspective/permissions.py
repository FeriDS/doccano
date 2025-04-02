from rest_framework.permissions import BasePermission, IsAuthenticated

class IsProjectAdmin(IsAuthenticated):
    """
    Permite acesso apenas a administradores de projeto
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff