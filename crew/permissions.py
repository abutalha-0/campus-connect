from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Allows read access to anyone, write access only to the object's owner.
    Checks author/user/requester in that order, whichever the model has.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None) or getattr(obj, 'requester', None)
        return owner == request.user
