from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework import permissions
from rest_framework import views, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from ..models import Round
from ..renderers import PlainTextRenderer
from ..permissions import IsAdmin


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

        return self.file_save_xml(request.data.get('file', ''), r, )

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