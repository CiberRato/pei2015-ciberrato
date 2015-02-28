from rest_framework import permissions

import sys


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        print >> sys.stderr, request.user.is_admin
        if request.user:
            return request.user.is_admin
        return False
