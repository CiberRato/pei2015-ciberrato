from django.shortcuts import get_object_or_404
from competition.models import Competition, Round
from competition.serializers import CompetitionSerializer, RoundSerializer
from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from competition.permissions import IsAdmin
from competition.views.simplex import RoundSimplex


class CompetitionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdmin(),

    def create(self, request, **kwargs):
        """
        B{Create} a competition
        B{URL:} ../api/v1/competitions/crud/

        @type  name: str
        @param name: The competition name
        @type  type_of_competition: Colaborativa | Competitiva
        @param type_of_competition: The competition type
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            Competition.objects.create(**serializer.validated_data)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'The competitions could not be created with received data'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the competition information
        B{URL:} ../api/v1/competitions/crud/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=kwargs.get('pk'))
        serializer = self.serializer_class(competition)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the competition
        B{URL:} ../api/v1/competitions/crud/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=kwargs.get('pk'))

        rounds = Round.objects.filter(parent_competition=competition)
        for r in rounds:
            r.delete()

        competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition has been deleted'},
                        status=status.HTTP_200_OK)


class CompetitionStateViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the competition information
        B{URL:} ../api/v1/competitions/get/<state>/

        @type  type: {'Past', 'Register', 'Competition', 'All'}
        @param type: dict
        """
        state = dict(Competition.STATE)

        if kwargs.get('pk') in state:
            queryset = Competition.objects.filter(state_of_competition=kwargs.get('pk'))
        elif kwargs.get('pk') == 'All':
            queryset = Competition.objects.all()
        else:
            return Response({'status': 'Bad Request',
                             'message': 'The state must mach: {\'Past\', \'Register\', \'Competition\', \'All\'}'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CompetitionRounds(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = RoundSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the competition rounds
        B{URL:} ../api/v1/competitions/rounds/<competition_name>/

        @type  competition_name: string
        @param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))
        serializer = self.serializer_class([RoundSimplex(r) for r in competition.round_set.all()], many=True)
        return Response(serializer.data)