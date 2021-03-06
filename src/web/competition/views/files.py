from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.db import transaction

from rest_framework import permissions
from rest_framework import views, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from ..models import Competition, Round
from ..renderers import PlainTextRenderer, JSONRenderer
from ..permissions import IsStaff

import xmltodict
import json


class GetRoundFile(views.APIView):
    renderer_classes = (PlainTextRenderer,)

    @staticmethod
    def get(request, competition_name, round_name, param):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round_file/<competition_name>/<round_name>/<param>/

        Get Round Files

        SERVER-TO-SERVER ONLY

        :type  competition_name: str
        :param competition_name: The agent name
        :type  round_name: str
        :param round_name: The team name
        :type  param: str
        :param param: The file type: param_list, lab, grid
        """
        if param != 'param_list' and param != 'lab' and param != 'grid':
            return Response({'status': 'Bad request',
                             'message': 'A valid *file*'},
                            status=status.HTTP_400_BAD_REQUEST)

        # see if round exists
        competition = get_object_or_404(Competition.objects.all(), name=competition_name)
        r = get_object_or_404(Round.objects.all(), name=round_name, parent_competition=competition)

        try:
            if bool(getattr(r, param + '_path', '')) and default_storage.exists(getattr(r, param + '_path', '')):
                data = default_storage.open(getattr(r, param + '_path', '')).read()
            else:
                return Response({'status': 'Bad request',
                                 'message': 'The file doesn\'t exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data)


class GetRoundResourcesFile(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def post(request):
        """
        B{Retrieve} the round resources files
        B{URL:} ../api/v1/competitions/resources_file/

        Permissions:
        - Must be authenticated

        POST
        Get resource Files in json

        :type  path: str
        :param path: The file path
        """
        path = request.data.get('path', None)

        if path is None:
            return Response({'status': 'Bad request',
                             'message': 'The file that you requested doesn\'t exists!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not default_storage.exists(path):
            return Response({'status': 'Bad request',
                             'message': 'The file that you requested doesn\'t exists!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if is a valid path
        if not path.startswith('resources/'):
            return Response({'status': 'Bad request',
                             'message': 'Invalid file!'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            data = default_storage.open(path).read()

            if 'param_list' in path:
                json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorParams)
            elif 'lab' in path:
                json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorLab)
            else:
                json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorGrid)

            json_data = json.dumps(json_obj)
            json_data = json_data.replace("@", "_")
            json_data = json_data.replace('"#text": "\\""', "")
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(json_data)


class GetRoundJsonFile(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    @staticmethod
    def get(request, competition_name, round_name, param):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round_json_file/<competition_name>/<round_name>/<param>/

        Get Round Files as json

        :type  competition_name: str
        :param competition_name: The agent name
        :type  round_name: str
        :param round_name: The team name
        :type  param: str
        :param param: The file type: param_list, lab, grid
        """
        if param != 'param_list' and param != 'lab' and param != 'grid':
            return Response({'status': 'Bad request',
                             'message': 'A valid *file*'},
                            status=status.HTTP_400_BAD_REQUEST)

        # see if round exists
        competition = get_object_or_404(Competition.objects.all(), name=competition_name)
        r = get_object_or_404(Round.objects.all(), name=round_name, parent_competition=competition)

        try:
            if bool(getattr(r, param + '_path', '')) and default_storage.exists(getattr(r, param + '_path', '')):
                data = default_storage.open(getattr(r, param + '_path', '')).read()

                if param == 'param_list':
                    json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorParams)
                elif param == 'lab':
                    json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorLab)
                else:
                    json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorGrid)

                json_data = json.dumps(json_obj)
                json_data = json_data.replace("@", "_")
                json_data = json_data.replace('"#text": "\\""', "")
            else:
                return Response({'status': 'Bad request',
                                 'message': 'The file doesn\'t exists!'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'status': 'Bad request',
                             'message': 'The file doesn\'t exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(json_data)


class UploadRoundXMLView(views.APIView):
    parser_classes = (FileUploadParser,)

    def __init__(self, file_to_save):
        views.APIView.__init__(self)
        self.file_to_save = file_to_save

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def post(self, request):
        if 'round' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?round=*round_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the &competition_name=*competition_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))
        r = get_object_or_404(Round.objects.all(), name=request.GET.get('round', ''), parent_competition=competition)

        return self.file_save_xml(request.data.get('file', ''), r, request)

    def file_save_xml(self, file_obj, r, request):
        if getattr(r, self.file_to_save+"_path", None) is not None and getattr(r, self.file_to_save+"_can_delete"):
            getattr(r, self.file_to_save+"_path", None).delete(False)

        if not isinstance(file_obj, InMemoryUploadedFile) and file_obj.size is 0:
            return Response({'status': 'Bad request',
                             'message': 'You must send a file!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > 102400:
            return Response({'status': 'Bad request',
                             'message': 'You can only upload files with size less than 100KB.'},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))
            r = get_object_or_404(Round.objects.all(), name=request.GET.get('round', ''), parent_competition=competition)

            setattr(r, self.file_to_save+"_path", file_obj)
            setattr(r, self.file_to_save + "_can_delete", True)
            r.save()

        return Response({'status': 'Uploaded',
                         'message': 'The file has been uploaded and saved to ' + str(r.name)},
                        status=status.HTTP_201_CREATED)


class UploadParamListView(UploadRoundXMLView):
    def __init__(self):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round/upload/param_list/?round=<round_name>&competition_name=<competition_name>

        Upload Param List

        :type  competition_name: str
        :param competition_name: The agent name
        :type  round_name: str
        :param round_name: The team name
        """
        UploadRoundXMLView.__init__(self, "param_list")


class UploadGridView(UploadRoundXMLView):
    def __init__(self):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round/upload/grid/?round=<round_name>&competition_name=<competition_name>

        Upload grid

        :type  competition_name: str
        :param competition_name: The agent name
        :type  round_name: str
        :param round_name: The team name
        """
        UploadRoundXMLView.__init__(self, "grid")


class UploadLabView(UploadRoundXMLView):
    def __init__(self):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round/upload/lab/?round=<round_name>&competition_name=<competition_name>

        Upload lab

        :type  competition_name: str
        :param competition_name: The agent name
        :type  round_name: str
        :param round_name: The team name
        """
        UploadRoundXMLView.__init__(self, "lab")


class UploadResourceFile(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def post(self, request, competition_name, round_name, param):
        """
        B{Set} the round file
        B{URL:} ../api/v1/set_round_file/<competition_name>/<round_name>/<param>/

        Upload resource

        :type  competition_name: str
        :param competition_name: The competition name
        :type  round_name: str
        :param round_name: The round name
        :type  param: str
        :param param: grid, lab or param_list
        :type  path: str
        :param path: The path to the file
        """
        path = request.data.get('path', None)

        if path is None:
            return Response({'status': 'Bad request',
                             'message': 'The file that you requested doesn\'t exists!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not default_storage.exists(path):
            return Response({'status': 'Bad request',
                             'message': 'The file that you requested doesn\'t exists!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verify if is a valid path
        if not path.startswith('resources/'):
            return Response({'status': 'Bad request',
                             'message': 'Invalid file!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if param not in ['grid', 'lab', 'param_list']:
            return Response({'status': 'Bad request',
                             'message': 'Please provide one of those params: grid, lab or param_list'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=competition_name)
        r = get_object_or_404(Round.objects.all(), name=round_name, parent_competition=competition)

        if bool(getattr(r, param + '_path', '')) and default_storage.exists(getattr(r, param + '_path', '')) \
                and getattr(r, param + "_can_delete"):
            default_storage.delete(getattr(r, param + "_path", None))

        setattr(r, param + "_path", default_storage.path(path))
        setattr(r, param + "_can_delete", False)
        r.save()

        return Response({'status': 'Uploaded',
                         'message': 'The file has been associated!'},
                        status=status.HTTP_201_CREATED)


class JsonListElements:
    def __init__(self):
        self.prevPath = None
        self.count = 0
        self.list = None
        self.lab = {'Corner': None, 'Wall': None, 'Beacon': None, 'Target': None}
        self.grid = {'Position': None}
        self.params = {}
        self.data = {'Robot': None, 'IRSensor': None}

    def postprocessorGrid(self, path, key, value):
        self.list = self.grid
        return self.postprocessor(path, key, value)

    def postprocessorLab(self, path, key, value):
        self.list = self.lab
        return self.postprocessor(path, key, value)

    def postprocessorParams(self, path, key, value):
        self.list = self.params
        return self.postprocessor(path, key, value)

    def postprocessor(self, path, key, value):
        if key in self.list.keys() and self.list[key] == None:
            self.list[key] = len(path)
            tupl = key, [value]
        else:
            tupl = key, value
        for key in self.list.keys():
            if self.list[key] != None and self.list[key] > len(path):
                self.list[key] = None
        return tupl