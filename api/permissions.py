from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class ObjReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # allow to all users to retrieve an object
        if request.method in ["GET"]:
            return True


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class AllowAuthPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["POST"]:
            return bool(request.user and request.user.is_authenticated)

        return False


class FullObjAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return bool(
                (request.user.is_admin or request.user.is_moderator)
                or request.user.is_superuser
                or obj.author == request.user
            )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_admin or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.is_superuser:
            return True
        return False


class IsUserSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False

    def has_object_permission(self, request, view, obj):
        if request.method not in ["GET", "PATCH"]:
            return False

        return obj == request.user
