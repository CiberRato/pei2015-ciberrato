# coding=utf-8
from rest_framework import permissions

from authentication.models import Group, GroupMember
from competition.models import Agent

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
        try:
            group_name = request.path.split("/")[-2:-1][0]
        except ValueError:
            return False

        group = Group.objects.filter(name=group_name)
        if len(group) == 0:
            if view.__class__.__name__ == 'MemberInGroupViewSet' and request.method == 'POST':
                try:
                    data = dict(request.data)
                    group_name = data['group_name']
                    group = Group.objects.filter(name=group_name)
                except AttributeError:
                    return False
            elif view.__class__.__name__ == 'EnrollGroup' and request.method == 'POST':
                try:
                    group_name = request.data['group_name']
                    group = Group.objects.filter(name=group_name)
                except AttributeError:
                    return False
            elif view.__class__.__name__ == 'AgentViewSets' and request.method == 'POST':
                try:
                    group_name = request.data['group_name']
                    group = Group.objects.filter(name=group_name)
                except AttributeError:
                    return False
            elif view.__class__.__name__ == 'AgentViewSets' and request.method == 'DELETE':
                try:
                    agent_name = request.path.split("/")[-2:-1][0]
                except ValueError:
                    return False
                try:
                    agent = Agent.objects.get(agent_name=agent_name)
                    group = agent.group
                except AttributeError:
                    return False
            elif 'group_name' in request.GET:
                group = Group.objects.filter(name=request.GET.get('group_name', ''))
                if len(group) == 0:
                    return False
            else:
                print request
                return False

        group_member = GroupMember.objects.filter(account=request.user, group=group)
        if len(group_member) >= 1:
            return group_member[0].is_admin
        return False