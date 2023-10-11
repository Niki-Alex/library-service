from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIsOwnerGetPost(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_staff)
            or (request.user
                and request.user.is_authenticated
                and request.method in SAFE_METHODS + ("POST",))
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and request.user.is_staff
            or (obj.user == request.user
                and request.method in SAFE_METHODS + ("POST",))
        )
