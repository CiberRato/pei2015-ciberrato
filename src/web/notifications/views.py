from rest_framework import permissions
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import OldAdminNotification, OldBroadcastNotification
from .serializers_views import OldAdminNotificationSerializer, OldBroadcastNotificationSerializer
from competition.permissions import IsStaff


class OldAdminNotificationList(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OldAdminNotification.objects.filter()
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
    queryset = OldBroadcastNotification.objects.filter()
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