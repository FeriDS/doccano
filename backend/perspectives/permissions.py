from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import ProjectPerspective, UserPerspectiveAnswer

class HasCompletePerspective(BasePermission):
    """
    Permission class to check if the project's perspective is complete
    before allowing annotations.
    """
    message = "You must complete the project's perspective before making annotations."

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
            
        project_id = view.kwargs.get('project_id')
        if not project_id:
            return False

        try:
            # Check if project has a perspective configured
            project_perspective = ProjectPerspective.objects.get(project_id=project_id)
            
            # Check if the user has completed their perspective answer
            user_answer = UserPerspectiveAnswer.objects.filter(
                project_perspective=project_perspective,
                user=request.user
            ).first()
            
            if not user_answer:
                self.message = "You need to complete the project's perspective before annotating."
                return False
                
            return user_answer.is_complete
            
        except ProjectPerspective.DoesNotExist:
            self.message = "This project doesn't have a perspective configured yet."
            return False 