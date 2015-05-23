import tempfile
import tarfile
from zipfile import ZipFile
import mimetypes

from hurry.filesize import size

from django.core.files.uploadedfile import InMemoryUploadedFile
from os.path import getsize

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from authentication.models import Team

from ..serializers import AgentSerializer, FileAgentSerializer, LanguagesSerializer
from ..models import Agent, AgentFile
from ..simplex import AgentFileSimplex
from teams.permissions import MustBeTeamMember

from rest_framework import permissions
from rest_framework import mixins, viewsets, views, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response


class UploadAgent(views.APIView):
    parser_classes = (FileUploadParser,)

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def post(request, *args, **kwargs):
        """
        B{Upload} an agent file
        B{URL:} ../api/v1/agents/upload/agent/?<agent_name>&team_name=<team_name>

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        """
        if 'agent_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?agent_name=<agent_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'team_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the &team_name=<team_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))

        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=request.GET.get('agent_name', ''))

        if agent.is_remote:
            return Response({'status': 'Bad request',
                             'message': 'You can\'t upload code to a virtual agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        MustBeTeamMember(user=request.user, team=team)

        file_obj = request.data.get('file', '')

        if not isinstance(file_obj, InMemoryUploadedFile) and file_obj.size is 0:
            return Response({'status': 'Bad request',
                             'message': 'You must send a file!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > settings.ALLOWED_UPLOAD_SIZE:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than: ' + size(
                                 settings.ALLOWED_UPLOAD_SIZE)},
                            status=status.HTTP_400_BAD_REQUEST)

        if AgentFile.objects.filter(agent=agent, original_name=file_obj.name).count() == 1:
            file_agent = AgentFile.objects.get(agent=agent, original_name=file_obj.name)
            file_agent.delete()

        try:
            with transaction.atomic():
                AgentFile.objects.create(agent=agent, file=file_obj, original_name=file_obj.name)
        except IntegrityError:
            return Response({'status': 'Bad request',
                             'message': 'The agent has already one file with that name!'},
                            status=status.HTTP_400_BAD_REQUEST)

        agent.code_valid = False
        agent.validation_result = ""
        agent.save()

        return Response({'status': 'File uploaded!',
                         'message': 'The agent code has been uploaded!'},
                        status=status.HTTP_201_CREATED)


class DeleteUploadedFileAgent(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} an agent file
        B{URL:} ../api/v1/agents/delete_agent_file/<agent_name>/?file_name=<file_name>&team_name=<team_name>

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        :type  file_name: str
        :param file_name: The file name
        """
        if 'team_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the &team_name=<team_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))
        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=kwargs.get('pk', ''))

        MustBeTeamMember(user=request.user, team=team)

        if 'file_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?file_name=*file_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(AgentFile.objects.all(), agent=agent,
                                     original_name=request.GET.get('file_name', ''))
        file_obj.delete()

        agent.code_valid = False
        agent.save()

        return Response({'status': 'Deleted',
                         'message': 'The agent file has been deleted'},
                        status=status.HTTP_200_OK)


class ListAgentsFiles(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = FileAgentSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the agent files list
        B{URL:} ../api/v1/agents/agent_files/<agent_name>/?team_name=<team_name>
        Must be part of the team owner of the agent

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  agent_name: str
        :param agent_name: The agent name
        """
        if 'team_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?team_name=<team_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        team = get_object_or_404(Team.objects.all(), name=request.GET.get('team_name', ''))
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'), team=team)

        MustBeTeamMember(user=request.user, team=team)

        files = []
        for file_obj in AgentFile.objects.filter(agent=agent):
            files += [AgentFileSimplex(file_obj)]

        serializer = self.serializer_class(files, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllAgentFiles(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def get(request, team_name, agent_name):
        """
        B{Retrieve} the agent files as zip
        B{URL:} ../api/v1/agents/agent_all_files/<team_name>/<agent_name>/
        Must be part of the team owner of the agent

        Client only

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=team_name)
        # agent_name
        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=agent_name)

        # see if user owns the agent
        MustBeTeamMember(user=request.user, team=team)

        if AgentFile.objects.filter(agent=agent).count() == 0:
            return Response({'status': 'Bad request',
                             'message': 'The agent doesn\'t have files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        temp = tempfile.NamedTemporaryFile()
        with ZipFile(temp.name, 'w') as z:
            for file_obj in AgentFile.objects.filter(agent=agent):
                z.write(default_storage.path(file_obj.file), arcname=file_obj.original_name)
            z.close()

        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=' + agent_name + '.zip'
        response['Content-Length'] = getsize(temp.name)
        temp.seek(0)
        return response


class GetAgentFilesSERVER(views.APIView):
    @staticmethod
    def get(request, team_name, agent_name):
        """
        B{Retrieve} the agent files as tar
        B{URL:} ../api/v1/agents/agent_file/<team_name>/<agent_name>/
        Must be part of the team owner of the agent

        Server to Server only

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        """
        team = get_object_or_404(Team.objects.all(), name=team_name)
        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=agent_name)

        if AgentFile.objects.filter(agent=agent).count() == 0:
            return Response({'status': 'Bad request',
                             'message': 'The agent doesn\'t have files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        temp = tempfile.NamedTemporaryFile()
        with tarfile.open(temp.name, "w:gz") as tar:
            for file_obj in AgentFile.objects.filter(agent=agent):
                tar.add(default_storage.path(file_obj.file), arcname=file_obj.original_name)
            tar.close()

        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type="application/x-compressed")
        response['Content-Disposition'] = 'attachment; filename=' + agent_name + '.tar.gz'
        response['Content-Length'] = getsize(temp.name)
        temp.seek(0)
        return response


class GetAgentFile(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def get(request, team_name, agent_name, file_name):
        """
        B{Retrieve} the agent files as tar
        B{URL:} ../api/v1/agents/file/<team_name>/<agent_name>/<file_name>/
        Must be part of the team owner of the agent

        Client only

        -> Permissions
        # TeamMember
            The current logged user must be one team member

        :type  agent_name: str
        :param agent_name: The agent name
        :type  team_name: str
        :param team_name: The team name
        :type  file_name: str
        :param file_name: The file name
        """
        team = get_object_or_404(Team.objects.all(), name=team_name)
        agent = get_object_or_404(Agent.objects.all(), team=team, agent_name=agent_name)

        if AgentFile.objects.filter(agent=agent).count() == 0:
            return Response({'status': 'Bad request',
                             'message': 'The agent doesn\'t have files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        MustBeTeamMember(user=request.user, team=team)

        file_obj = get_object_or_404(AgentFile.objects.all(), agent=agent, original_name=file_name)

        wrapper = FileWrapper(default_storage.open(file_obj.file))
        response = HttpResponse(wrapper, content_type=mimetypes.guess_type(default_storage.path(file_obj.file)))
        response['Content-Disposition'] = 'attachment; filename=' + file_obj.original_name
        response['Content-Length'] = getsize(default_storage.path(file_obj.file))
        return response


class GetAllowedLanguages(views.APIView):
    serializer_class = LanguagesSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request):
        """
        B{Get} the allowed languages
        B{URL:} ../api/v1/agents/allowed_languages/
        """

        class Language:
            def __init__(self, name, value):
                self.name = name
                self.value = value

        languages = []
        for key, value in dict(settings.ALLOWED_UPLOAD_LANGUAGES).iteritems():
            languages += [Language(key, value)]

        serializer = self.serializer_class(languages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
