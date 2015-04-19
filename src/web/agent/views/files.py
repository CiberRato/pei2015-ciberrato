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
from authentication.models import GroupMember
from ..serializers import AgentSerializer, FileAgentSerializer, LanguagesSerializer
from ..models import Agent, AgentFile
from ..simplex import AgentFileSimplex
from rest_framework import permissions
from rest_framework import mixins, viewsets, views, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response


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

        agent = get_object_or_404(Agent.objects.all(), agent_name=request.GET.get('agent_name', ''))

        if agent.is_local:
            return Response({'status': 'Bad request',
                             'message': 'You can\'t upload code to a virtual agent!'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.filter(group=agent.group, account=request.user)

        if len(group_member) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

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

        try:
            with transaction.atomic():
                AgentFile.objects.create(agent=agent, file=file_obj, original_name=file_obj.name)
        except IntegrityError:
            return Response({'status': 'Bad request',
                             'message': 'The agent has already one file with that name!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # call code validations
        """
        try:
            requests.get(settings.TEST_CODE_ENDPOINT.replace("<agent_name>", agent.agent_name))
        except requests.ConnectionError:
            agent.code_valid = False
            agent.validation_result = "The endpoint to do the code validation is down!"
            agent.save()
        """

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
        B{URL:} ../api/v1/agents/delete_agent_file/<agent_name>/?file_name=<file_name>

        @type  agent_name: str
        @param agent_name: The agent name
        @type  file_name: str
        @param file_name: The file name
        """
        agent = get_object_or_404(Agent.objects.all(), agent_name=kwargs.get('pk'))

        if len(GroupMember.objects.filter(group=agent.group, account=request.user)) == 0:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        if 'file_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?file_name=*file_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(AgentFile.objects.all(), agent=agent,
            original_name=request.GET.get('file_name', ''))
        file_obj.delete()

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
        B{URL:} ../api/v1/agents/agent_files/<agent_name>/
        Must be part of the group owner of the agent

        @type  agent_name: str
        @param agent_name: The agent name
        """
        agent = get_object_or_404(self.queryset, agent_name=kwargs.get('pk'))

        if len(GroupMember.objects.filter(group=agent.group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        files = []
        for file_obj in AgentFile.objects.filter(agent=agent):
            files += [AgentFileSimplex(file_obj)]

        serializer = self.serializer_class(files, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllAgentFiles(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def get(request, agent_name):
        # agent_name
        agent = get_object_or_404(Agent.objects.all(), agent_name=agent_name)

        # see if user owns the agent
        if len(GroupMember.objects.filter(group=agent.group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

        if len(AgentFile.objects.filter(agent=agent)) == 0:
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
    def get(request, agent_name):
        # agent_name
        agent = get_object_or_404(Agent.objects.all(), agent_name=agent_name)

        if len(AgentFile.objects.filter(agent=agent)) == 0:
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
    @staticmethod
    def get(request, agent_name, file_name):
        # agent_name
        agent = get_object_or_404(Agent.objects.all(), agent_name=agent_name)

        if len(AgentFile.objects.filter(agent=agent)) == 0:
            return Response({'status': 'Bad request',
                             'message': 'The agent doesn\'t have files.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # see if user owns the agent
        if len(GroupMember.objects.filter(group=agent.group, account=request.user)) != 1:
            return Response({'status': 'Permission denied',
                             'message': 'You must be part of the group.'},
                            status=status.HTTP_403_FORBIDDEN)

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
