from rest_framework import permissions

from authentication.models import Account

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):

        account = Account.objects.filter(account = request.user, is_admin=True)

        if account.len >= 1:
            return account.is_admin

        return False
