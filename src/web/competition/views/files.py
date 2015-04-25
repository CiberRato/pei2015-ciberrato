from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.db import transaction

from rest_framework import permissions
from rest_framework import views, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from ..models import Competition, Round
from ..renderers import PlainTextRenderer
from ..permissions import IsStaff


class GetRoundFile(views.APIView):
    renderer_classes = (PlainTextRenderer,)

    @staticmethod
    def get(request, competition_name, round_name, param):
        """
        B{Retrieve} the round files
        B{URL:} ../api/v1/competitions/round_file/<competition_name>/<round_name>/<param>/

        Get Round Files

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


class UploadRoundXMLView(views.APIView):
    parser_classes = (FileUploadParser,)

    def __init__(self, file_to_save, folder):
        views.APIView.__init__(self)
        self.file_to_save = file_to_save
        self.folder = folder

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
        if getattr(r, self.file_to_save, None) is not None:
            getattr(r, self.file_to_save, None).delete(False)

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

            setattr(r, self.file_to_save, file_obj)
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
        UploadRoundXMLView.__init__(self, "param_list_path", "param_list")


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
        UploadRoundXMLView.__init__(self, "grid_path", "grid")


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
        UploadRoundXMLView.__init__(self, "lab_path", "lab")