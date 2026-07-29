from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Allows access only to authenticated users with the STUDENT role."""
    message = 'Only students can perform this action.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, 'role', None) == 'STUDENT'
        )


class IsVerifiedFaculty(BasePermission):
    """
    Allows access only to authenticated faculty whose account has been
    verified by the admin office. Shared across classroom apps (subjects,
    classes, …) since they all require a verified faculty to create content.
    """
    message = 'Your faculty account must be verified before you can do this.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, 'role', None) != 'FACULTY' or not hasattr(user, 'faculty_profile'):
            self.message = 'Only faculty members can perform this action.'
            return False

        if not user.faculty_profile.is_verified:
            self.message = (
                'Your faculty account is pending verification by the admin '
                'office. You cannot add subjects until it is verified.'
            )
            return False

        return True
