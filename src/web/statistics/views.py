from django.core.files.storage import default_storage

from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from competition.permissions import IsStaff
from competition.models import AgentFile
from .serializers import MediaStatsSerializer
from hurry.filesize import size

import os


class MediaStats(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AgentFile.objects.filter()
    serializer_class = MediaStatsSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def list(self, request, *args, **kwargs):
        """
        B{List} the media size dir
        B{URL:} ../api/v1/statistics/media/
        """
        class MediaDir:
            def __init__(self, agents, grids, json_logs, labs, params):
                self.agents = agents
                self.grids = grids
                self.json_logs = json_logs
                self.labs = labs
                self.params = params

        agents_size = size(self._total_size(default_storage.path('agents')))
        grids_size = size(self._total_size(default_storage.path('grids')))
        json_logs_size = size(self._total_size(default_storage.path('json_logs')))
        labs_size = size(self._total_size(default_storage.path('labs')))
        params_size = size(self._total_size(default_storage.path('params')))

        media_dir = MediaDir(agents_size, grids_size, json_logs_size, labs_size, params_size)

        serializer = self.serializer_class(media_dir)
        return Response(serializer.data)

    def _total_size(self, source):
        total_size = os.path.getsize(source)
        for item in os.listdir(source):
            itempath = os.path.join(source, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += self._total_size(itempath)
        return total_size