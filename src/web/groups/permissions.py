# coding=utf-8
from rest_framework import permissions

from authentication.models import Group, GroupMember
from django.shortcuts import get_object_or_404


class IsAdminOfGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        If the GroupMember is admin of Group.

        @type  request: WSGIRequest
        @param request: WSGIRequest (https://github.com/django/django/blob/master/django/core/handlers/wsgi.py)
        Django’s primary deployment platform is WSGI, the Python standard for web servers and applications
            https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/

        @type  view: ViewSets
        @param view: http://www.django-rest-framework.org/api-guide/viewsets/

        @rtype:   Boolean
        @return:  True if the user has permission else False
        """
        group_name = request.path.split("/")[-2:-1][0]
        group = get_object_or_404(Group.objects.all(), name=group_name)
        group_member = GroupMember.objects.filter(account=request.user, group=group)
        if len(group_member) >= 1:
            return group_member[0].is_admin
        return False

    def has_object_permission(self, request, view, obj):
        """
        Note: The instance-level has_object_permission method will only be called if the view-level
        has_permission checks have already passed.

        @type  request: WSGIRequest
        @param request: Above ^

        @type  view: ViewSets
        @param view: Above ^

        @type  obj: GroupMember
        @param obj: authentication.GroupMember

        @rtype:   Boolean
        @return:  True if the object has permissions else False
        """
        if isinstance(obj, GroupMember):
            user = GroupMember.objects.filter(account=request.user, group=obj.group)
            if len(user) >= 1:
                return user[0].is_admin
        return False