from rest_framework.permissions import BasePermission, IsAdminUser as DRFIsAdminUser
from django.conf import settings
from projects.models import Member


class RolePermission(BasePermission):
    UNSAFE_METHODS = ("POST", "PATCH", "DELETE")
    unsafe_methods_check = True
    role_name = ""

    @classmethod
    def get_project_id(cls, request, view):
        return view.kwargs.get("project_id") or request.query_params.get("project_id")

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True

        if self.unsafe_methods_check and request.method in self.UNSAFE_METHODS:
            return False

        project_id = self.get_project_id(request, view)
        if not project_id and request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return Member.objects.has_role(project_id, request.user, self.role_name)


class IsAdminUser(DRFIsAdminUser):
    """
    Usa o IsAdminUser nativo do DRF.
    """
    pass


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


IsProjectMember = IsAnnotator | IsAnnotationApprover | IsProjectAdmin  # type: ignore
IsProjectStaffAndReadOnly = IsAnnotatorAndReadOnly | IsAnnotationApproverAndReadOnly  # type: ignore