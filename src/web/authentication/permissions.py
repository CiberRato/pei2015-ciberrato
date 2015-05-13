from rest_framework import permissions
from ciberonline.exceptions import Forbidden


class IsAccountOwner(permissions.BasePermission):
    """
    Verify if user is the Account Owner
    """

    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj == request.user

        return False


class MustBeStaffUser:
    def __init__(self, user, message):
        if user.is_staff is False:
            raise Forbidden(message)


class UserIsUser:
    def __init__(self, user, instance, message):
        if instance != user:
            raise Forbidden(message)
