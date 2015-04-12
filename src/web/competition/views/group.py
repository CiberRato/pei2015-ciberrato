from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from django.db import transaction

from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from groups.serializers import GroupSerializer
from groups.permissions import IsAdminOfGroup

from ..permissions import IsStaff
from .simplex import RoundSimplex, GroupEnrolledSimplex
from ..models import Competition, Round, GroupEnrolled
from ..serializers import RoundSerializer, GroupEnrolledSerializer, GroupEnrolledOutputSerializer, \
    CompetitionSerializer

from authentication.models import Group
from authentication.models import Account


class CompetitionGetGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupEnrolledOutputSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled and with valid inscription or not in the Competition
        B{URL:} ../api/v1/competitions/groups/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))
        serializer = self.serializer_class(competition.groupenrolled_set.all(), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyEnrolledGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled
        B{URL:} ../api/v1/competitions/my_enrolled_groups/<username>/

        @type  username: str
        @param username: The username
        """
        user = get_object_or_404(Account.objects.all(), username=kwargs.get('pk'))

        enrolled_groups = []
        for group in user.groups.all():
            for eg in group.groupenrolled_set.all():
                enrolled_groups += [GroupEnrolledSimplex(eg)]

        serializer = self.serializer_class(enrolled_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionGetNotValidGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled with inscription not valid in the Competition
        B{URL:} ../api/v1/competitions/groups_not_valid/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))
        not_valid = GroupEnrolled.objects.filter(valid=False, competition=competition)
        not_valid_groups = [g.group for g in not_valid]
        serializer = self.serializer_class(not_valid_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionOldestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the oldest round competition
        B{URL:} ../api/v1/competitions/first_round/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if len(competition.round_set.all()) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition.round_set.all().reverse()[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionEarliestRoundViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the earliest round competition
        B{URL:} ../api/v1/competitions/earliest_round/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))

        if len(competition.round_set.all()) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition.round_set.all()[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class ToggleGroupValid(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = GroupEnrolled.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def create(self, request, *args, **kwargs):
        """
        B{Toggle} the Group Enrolled inscription
        B{URL:} ../api/v1/competitions/toggle_group_inscription/

        @type  competition_name: str
        @param competition_name: The Competition name
        @type  group_name: str
        @param group_name: The Group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                name=serializer.validated_data['competition_name'])
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            group_enrolled = get_object_or_404(GroupEnrolled.objects.all(), competition=competition, group=group)
            group_enrolled.valid = not group_enrolled.valid
            group_enrolled.save()

            return Response({'status': 'Inscription toggled!',
                             'message': 'Inscription is now: ' + str(group_enrolled.valid)},
                            status=status.HTTP_200_OK)

        return Response({'status': 'Bad request',
                         'message': 'The group can\'t enroll with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)


class MyEnrolledGroupsInCompetitionViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled by username and competition
        B{URL:} ../api/v1/competitions/my_enrolled_groups_competition/<username>/?competition_name=<competition_name>

        @type  username: str
        @param username: The username
        @type  competition_name: str
        @param competition_name: The competition name
        """
        user = get_object_or_404(Account.objects.all(), username=kwargs.get('pk'))
        competition = get_object_or_404(Competition.objects.all(), name=request.GET.get('competition_name', ''))

        enrolled_groups = []
        for group in user.groups.all():
            enrolled_group = GroupEnrolled.objects.filter(group=group, competition=competition)
            if len(enrolled_group) == 1:
                enrolled_groups += [GroupEnrolledSimplex(enrolled_group[0])]

        serializer = self.serializer_class(enrolled_groups, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetEnrolledGroupCompetitionsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of competitions enrolled and with valid inscription by group
        B{URL:} ../api/v1/competitions/group_enrolled_competitions/<group_name>/

        @type  group_name: str
        @param group_name: The group name
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        groups = GroupEnrolled.objects.filter(group=group, valid=True)

        competitions = []
        for group_enrolled in groups:
            competitions += [group_enrolled.competition]

        serializer = self.serializer_class(competitions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollGroup(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                  mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GroupEnrolled.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def list(self, request, **kwargs):
        """
        B{List} the enrolled groups
        B{URL:} ../api/v1/competitions/enroll/
        """
        serializer = self.serializer_class([GroupEnrolledSimplex(ge=query) for query in GroupEnrolled.objects.all()],
                                           many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Get} the valid inscriptions in one competition for the group
        B{URL:} ../api/v1/competitions/enroll/<group_name>/

        @type  competition_name: str
        @param competition_name: The Competition name
        @type  group_name: str
        @param group_name: The Group name
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        group_enrolled = get_list_or_404(GroupEnrolled.objects.all(), group=group, valid=True)
        serializer = self.serializer_class([GroupEnrolledSimplex(group) for group in group_enrolled], many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """
        B{Create} a Group Enrolled to a competition
        B{URL:} ../api/v1/competitions/enroll/

        @type  competition_name: str
        @param competition_name: The Competition name
        @type  group_name: str
        @param group_name: The Group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            competition = get_object_or_404(Competition.objects.all(),
                name=serializer.validated_data['competition_name'])
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])

            if competition.state_of_competition != "Register":
                return Response({'status': 'Not allowed',
                                 'message': 'The group can\'t enroll in the competition.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            try:
                with transaction.atomic():
                    GroupEnrolled.objects.create(competition=competition, group=group)
            except IntegrityError:
                return Response({'status': 'Bad request',
                                 'message': 'The group already enrolled.'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'Created',
                             'message': 'The group has enrolled.'},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': 'The group can\'t enroll with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Remove} a group from the competition
        B{URL:} ../api/v1/competitions/enroll/<competition_name>/?group_name=<group_name>

        @type  competition_name: str
        @param competition_name: The competition name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'group_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?group_name=*group_name*'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))
        group = get_object_or_404(Group.objects.all(), name=request.GET.get('group_name', ''))

        group_not_enrolled = (len(GroupEnrolled.objects.filter(competition=competition, group=group)) == 0)

        if group_not_enrolled:
            return Response({'status': 'Bad request',
                             'message': 'The group is not enrolled in the competition'},
                            status=status.HTTP_400_BAD_REQUEST)

        # validations update values
        competition = get_object_or_404(Competition.objects.all(), name=kwargs.get('pk'))
        group = get_object_or_404(Group.objects.all(), name=request.GET.get('group_name', ''))

        group_enrolled = GroupEnrolled.objects.get(competition=competition, group=group)
        group_enrolled.delete()

        return Response(status=status.HTTP_200_OK)