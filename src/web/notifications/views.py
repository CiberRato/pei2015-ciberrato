from rest_framework import permissions
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import OldAdminNotification, OldBroadcastNotification, OldNotificationUser, OldNotificationTeam
from .serializers_views import OldAdminNotificationSerializer, OldBroadcastNotificationSerializer, \
    OldNotificationUserSerializer, OldNotificationTeamSerializer
from competition.permissions import IsStaff


class OldAdminNotificationList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OldAdminNotification.objects.all()
    serializer_class = OldAdminNotificationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the old admin notifications
        B{URL:} ../api/v1/notifications/admin/
        """
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class OldBroadcastNotificationList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OldBroadcastNotification.objects.all()
    serializer_class = OldBroadcastNotificationSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the old broadcast notifications
        B{URL:} ../api/v1/notifications/broadcast/
        """
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class OldNotificationUserList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OldNotificationUser.objects.all()
    serializer_class = OldNotificationUserSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the old user notifications
        B{URL:} ../api/v1/notifications/user/
        """
        serializer = self.serializer_class(self.queryset.filter(user=request.user), many=True)
        return Response(serializer.data)


class OldNotificationTeamList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OldNotificationTeam.objects.all()
    serializer_class = OldNotificationTeamSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the old user notifications
        B{URL:} ../api/v1/notifications/teams/
        """
        class TeamNotifications:
            def __init__(self, team, notifications):
                self.team = team
                self.notifications = notifications

        teams = []

        for team in request.user.teams.all():
            teams += [TeamNotifications(team=team, notifications=OldNotificationTeam.objects.filter(team=team))]

        serializer = self.serializer_class(teams, many=True)
        return Response(serializer.data)