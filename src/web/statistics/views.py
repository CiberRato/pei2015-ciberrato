from django.core.files.storage import default_storage

from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from competition.permissions import IsStaff
from competition.models import AgentFile
from .serializers import MediaStatsSerializer
from hurry.filesize import size


class MediaStats(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AgentFile.objects.filter(active=True)
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

        agents_size = size(default_storage('agents').size())
        grids_size = size(default_storage('grids').size())
        json_logs_size = size(default_storage('json_logs').size())
        labs_size = size(default_storage('labs').size())
        params_size = size(default_storage('params').size())

        media_dir = MediaDir(agents_size, grids_size, json_logs_size, labs_size, params_size)

        serializer = self.serializer_class(media_dir)
        return Response(serializer.data)