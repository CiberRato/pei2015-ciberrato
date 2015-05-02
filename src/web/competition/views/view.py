from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from ..permissions import IsStaff
from .simplex import RoundSimplex
from ..models import Competition, TypeOfCompetition
from ..serializers import CompetitionSerializer, CompetitionInputSerializer, RoundSerializer, \
    CompetitionStateSerializer, TypeOfCompetitionSerializer


class CompetitionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionInputSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, **kwargs):
        """
        B{Create} a competition
        B{URL:} ../api/v1/competitions/crud/

        :type  name: str
        :param name: The competition name
        :type  type_of_competition: The name of the type of competition
        :param type_of_competition: The competition type
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            type_of_competition = get_object_or_404(TypeOfCompetition.objects.all(),
                                                    name=serializer.validated_data['type_of_competition'])

            try:
                with transaction.atomic():
                    Competition.objects.create(name=serializer.validated_data['name'],
                                               type_of_competition=type_of_competition,
                                               allow_remote_agents=serializer.validated_data['allow_remote_agents'])
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'There is already a competition with that name.'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the competition information
        B{URL:} ../api/v1/competitions/crud/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))

        if competition.type_of_competition.name == "Private Competition":
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be seen!'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = CompetitionSerializer(competition)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the competition
        B{URL:} ../api/v1/competitions/crud/<competition_name>/

        :type  competition_name: str
        :param competition_name: The competition name
        """
        queryset = Competition.objects.all()
        competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))

        if competition.type_of_competition.name == "Private Competition":
            return Response({'status': 'Bad Request',
                             'message': 'This grid can\'t be deleted!'},
                            status=status.HTTP_400_BAD_REQUEST)

        for r in competition.round_set.all():
            r.delete()

        competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The competition has been deleted'},
                        status=status.HTTP_200_OK)


class CompetitionChangeState(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionStateSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the competition state
        B{URL:} ../api/v1/competitions/state/<name>/

        :type  state_of_competition: {'Past', 'Register', 'Competition'}
        :param state_of_competition: dict
        :type  name: str
        :param name: the competition name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(self.queryset, name=kwargs.get('pk', ''))

            if competition.type_of_competition.name == "Private Competition":
                return Response({'status': 'Bad Request',
                                 'message': 'This competition can\'t be changed!'},
                                status=status.HTTP_400_BAD_REQUEST)

            competition.state_of_competition = serializer.data.get('state_of_competition', '')
            competition.save()

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class CompetitionStateViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the competition information
        B{URL:} ../api/v1/competitions/get/<state>/

        :type  type: {'Past', 'Register', 'Competition', 'All'}
        :param type: dict
        """
        state = dict(Competition.STATE)

        try:
            toc = TypeOfCompetition.objects.get(name="Private Competition")
        except TypeOfCompetition.DoesNotExist:
            toc = TypeOfCompetition.objects.create(name="Private Competition", number_teams_for_trial=1,
                                                   number_agents_by_grid=50, single_position=False,
                                                   timeout=0)
        if kwargs.get('pk', '') in state:
            queryset = Competition.objects.filter(state_of_competition=kwargs.get('pk', '')).exclude(type_of_competition=toc)
        elif kwargs.get('pk', '') == 'All':
            queryset = Competition.objects.all().exclude(type_of_competition=toc)
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

        :type  competition_name: string
        :param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk', ''))

        if competition.type_of_competition.name == "Private Competition":
            team_owner = False
            for team in request.user.teams.all():
                for enroll in team.teamenrolled_set.all():
                    if enroll.competition == competition:
                        team_owner = True
                        break
                if team_owner:
                    break

            if not team_owner:
                return Response({'status': 'Bad request',
                                 'message': 'You can not see the rounds for this competition!'},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class([RoundSimplex(r) for r in competition.round_set.all()], many=True)
        return Response(serializer.data)


class TypeOfCompetitionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                               mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TypeOfCompetition.objects.all()
    serializer_class = TypeOfCompetitionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Create} type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/

        :type  name: str
        :param name: The type of competition name
        :type  number_teams_for_trial: Integer
        :type  number_teams_for_trial: The number of teams allowed by trial
        :type  number_agents_by_grid: Integer
        :param number_agents_by_grid: For each team the number of agents allowed by grid
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data['name'] == 'Private Competition':
                return Response({'status': 'Bad request',
                                 'message': 'This type of competition name is reserved!'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    TypeOfCompetition.objects.create(**serializer.validated_data)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'That type of competition was already created!'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/<type_of_competition_name>/

        :type  type_of_competition_name: str
        :param type_of_competition_name: The type_of_competition name
        """
        queryset = TypeOfCompetition.objects.all()
        type_of_competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))
        serializer = self.serializer_class(type_of_competition)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the type of competition
        B{URL:} ../api/v1/competitions/type_of_competition/<type_of_competition_name>/

        :type  type_of_competition_name: str
        :param type_of_competition_name: The type_of_competition name
        """
        queryset = TypeOfCompetition.objects.all()

        if kwargs.get('pk', '') == 'Private Competition':
            return Response({'status': 'Bad request',
                             'message': 'This type of competition is reserved!'},
                            status=status.HTTP_400_BAD_REQUEST)

        type_of_competition = get_object_or_404(queryset, name=kwargs.get('pk', ''))

        type_of_competition.delete()

        return Response({'status': 'Deleted',
                         'message': 'The type of competition has been deleted'},
                        status=status.HTTP_200_OK)