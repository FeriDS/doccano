from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Member, ProjectPerspective, UserPerspectiveAnswer


class RolePermission(BasePermission):
    UNSAFE_METHODS = ("POST", "PATCH", "DELETE")
    unsafe_methods_check = True
    role_name = ""

    @classmethod
    def get_project_id(cls, request, view):
        return view.kwargs.get("project_id") or request.query_params.get("project_id")

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if self.unsafe_methods_check and request.method in self.UNSAFE_METHODS:
            return request.user.is_superuser

        project_id = self.get_project_id(request, view)
        if not project_id and request.method in SAFE_METHODS:
            return True

        return Member.objects.has_role(project_id, request.user, self.role_name)


class IsProjectAdmin(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_PROJECT_ADMIN


class IsAnnotatorAndReadOnly(RolePermission):
    role_name = settings.ROLE_ANNOTATOR


class IsAnnotator(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_ANNOTATOR


class IsAnnotationApproverAndReadOnly(RolePermission):
    role_name = settings.ROLE_ANNOTATION_APPROVER


class IsAnnotationApprover(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_ANNOTATION_APPROVER


class IsAnnotatorAndHasValidPerspective(IsAnnotator):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        project_id = self.get_project_id(request, view)
        if not project_id:
            return False

        try:
            perspective = ProjectPerspective.objects.get(project_id=project_id)
            if not perspective.is_required:
                return True

            # Get all required fields
            required_fields = perspective.fields.filter(required=True)
            if not required_fields.exists():
                return True

            # Check if user has answered all required fields
            answered_fields = UserPerspectiveAnswer.objects.filter(
                user=request.user,
                project_id=project_id,
                field__in=required_fields
            ).values_list('field_id', flat=True)

            return set(required_fields.values_list('id', flat=True)) <= set(answered_fields)

        except ProjectPerspective.DoesNotExist:
            return True


IsProjectMember = IsAnnotator | IsAnnotationApprover | IsProjectAdmin  # type: ignore
IsProjectStaffAndReadOnly = IsAnnotatorAndReadOnly | IsAnnotationApproverAndReadOnly  # type: ignore
