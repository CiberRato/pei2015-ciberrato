import json
import tempfile
import tarfile

import os
from django.shortcuts import get_object_or_404
from competition.models import Round, Simulation, Agent
from competition.serializers import AgentSerializer
from authentication.models import GroupMember
from rest_framework import permissions
from rest_framework import mixins, viewsets, views, status
from competition.renderers import PlainTextRenderer
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from competition.permissions import IsAdmin
from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from os.path import basename
from rest_framework.renderers import JSONRenderer


class DeleteUploadedFileAgent(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent file
        B{URL:} ../api/v1/competitions/delete_agent_file/<agent_name>/?file_name=<file_name>

        @type  agent_name: str
        @param agent_name: The agent name
        @type  file_name: str
        @param file_name: The file name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))
        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)

        if len(group_member) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        if 'file_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?file_name=*file_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        if default_storage.exists('competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name',
                                                                                                         '')):
            load = json.loads(agent.locations)
            load.remove('competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name', ''))
            agent.locations = json.dumps(load)
            agent.save()
            default_storage.delete(
                'competition_files/agents/' + agent.agent_name + '/' + request.GET.get('file_name', ''))
            return Response({'status': 'Deleted',
                             'message': 'The agent file has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Not found',
                             'message': 'The agent file has not been found!'},
                            status=status.HTTP_404_NOT_FOUND)


class GetAllowedLanguages(views.APIView):
    @staticmethod
    def get(request):
        """
        B{Get} the allowed languages
        B{URL:} ../api/v1/competitions/allowed_languages/
        """
        return Response(JSONRenderer().render(settings.ALLOWED_UPLOAD_LANGUAGES), status=status.HTTP_200_OK)


class GetAgentsFiles(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the agent files list
        B{URL:} ../api/v1/competitions/agent_files/<agent_name>/

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))
        files = []

        for f in json.loads(agent.locations):
            files += [basename(f)]

        return Response(JSONRenderer().render(files), status=status.HTTP_200_OK)


class UploadAgent(views.APIView):
    parser_classes = (FileUploadParser,)

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def post(request):
        if 'agent_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?agent_name=*agent_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'language' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?language=*language*'},
                            status=status.HTTP_400_BAD_REQUEST)

        allowed_languages = dict(settings.ALLOWED_UPLOAD_LANGUAGES).values()
        if request.GET.get('language', '') not in allowed_languages:
            return Response({'status': 'Bad request',
                             'message': 'The uploaded language is not allowed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent.objects.all(), agent_name=request.GET.get('agent_name', ''))

        if agent.is_virtual:
            return Response({'status': 'Bad request',
                             'message': 'You can\'t upload code to a virtual agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)

        if len(group_member) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        file_obj = request.data['file']

        # language agent
        agent.language = request.GET.get('language', '')

        if file_obj.size > settings.ALLOWED_UPLOAD_SIZE:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than' + str(
                                 settings.ALLOWED_UPLOAD_SIZE) + "kb."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not agent.locations:
            load = []
        else:
            load = json.loads(agent.locations)

        path = default_storage.save('competition_files/agents/' + agent.agent_name + '/' + file_obj.name,
                                    ContentFile(file_obj.read()))

        load += [path]
        agent.locations = json.dumps(load)
        agent.save()

        return Response({'status': 'File uploaded!',
                         'message': 'The agent code has been uploaded!'},
                        status=status.HTTP_201_CREATED)


class GetRoundFile(views.APIView):
    renderer_classes = (PlainTextRenderer,)

    @staticmethod
    def get(request, round_name):
        if 'file' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?file=*file*'},
                            status=status.HTTP_400_BAD_REQUEST)

        param = request.QUERY_PARAMS.get('file')

        if param != 'param_list' and param != 'lab' and param != 'grid':
            return Response({'status': 'Bad request',
                             'message': 'A valid *file*'},
                            status=status.HTTP_400_BAD_REQUEST)

        # see if round exists
        r = get_object_or_404(Round.objects.all(), name=round_name)
        try:
            data = default_storage.open(getattr(r, param + '_path', None)).read()
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data)


class GetAgentFiles(views.APIView):
    @staticmethod
    def get(request, simulation_id, agent_name):
        # agent_name
        agent = get_object_or_404(Agent.objects.all(), agent_name=agent_name)

        # simulation_id
        simulation = get_object_or_404(Simulation.objects.all(), identifier=simulation_id)

        # see if round is in agent rounds
        if simulation.round not in agent.rounds.all():
            return Response({'status': 'Bad request',
                             'message': 'The agent is not in this round.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not agent.locations or len(json.loads(agent.locations)) == 0:
            return Response({'status': 'Bad request',
                             'message': 'The agent doesn\'t have files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        temp = tempfile.NamedTemporaryFile()
        with tarfile.open(temp.name, "w:gz") as tar:
            for name in json.loads(agent.locations):
                tar.add(default_storage.path(name), arcname=basename(default_storage.path(name)))
            tar.close()

        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type="application/x-compressed")
        response['Content-Disposition'] = 'attachment; filename=' + simulation_id + agent_name + '.tar.gz'
        response['Content-Length'] = os.path.getsize(temp.name)
        temp.seek(0)
        return response


class UploadRoundXMLView(views.APIView):
    parser_classes = (FileUploadParser,)

    def __init__(self, file_to_save, folder):
        views.APIView.__init__(self)
        self.file_to_save = file_to_save
        self.folder = folder

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def post(self, request):
        if 'round' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?round=*round_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round', ''))

        return self.file_save_xml(request.data['file'], r, )

    def file_save_xml(self, file_obj, r):
        if getattr(r, self.file_to_save, None) is not None:
            getattr(r, self.file_to_save, None).delete(False)

        if file_obj.size > 102400:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than 100KB.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if file_obj.content_type != 'application/xml':
            return Response({'status': 'Bad request',
                             'message': 'You can only upload XML files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save('competition_files/' + self.folder + '/' + file_obj.name,
                                    ContentFile(file_obj.read()))

        setattr(r, self.file_to_save, path)
        r.save()

        return Response({'status': 'Uploaded',
                         'message': 'The file has been uploaded and saved to ' + str(r.name)},
                        status=status.HTTP_201_CREATED)


class UploadParamListView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "param_list_path", "param_list")


class UploadGridView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "grid_path", "grid")


class UploadLabView(UploadRoundXMLView):
    def __init__(self):
        UploadRoundXMLView.__init__(self, "lab_path", "lab")