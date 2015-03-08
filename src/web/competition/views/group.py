from django.shortcuts import get_object_or_404
from competition.models import Competition, Round, GroupEnrolled
from competition.serializers import RoundSerializer, GroupEnrolledSerializer
from django.db import IntegrityError
from django.db import transaction
from authentication.models import Group
from groups.serializers import GroupSerializer
from rest_framework import permissions
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from competition.permissions import IsAdmin
from groups.permissions import IsAdminOfGroup
from competition.views.simplex import RoundSimplex, GroupEnrolledSimplex


class CompetitionGetGroupsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the list of a Groups enrolled and with valid inscription in the Competition
        B{URL:} ../api/v1/competitions/groups/<competition_name>/

        @type  competition_name: str
        @param competition_name: The competition name
        """
        competition = get_object_or_404(self.queryset, name=kwargs.get('pk'))
        valid = GroupEnrolled.objects.filter(valid=True, competition=competition)
        valid_groups = [g.group for g in valid]
        serializer = self.serializer_class(valid_groups, many=True)

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


class CompetitionGroupValidViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = GroupEnrolled.objects.all()
    serializer_class = GroupEnrolledSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAdmin(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the group enrolled attribute to valid or to false (it's a toggle)
        B{URL:} ../api/v1/competitions/group_valid/<group_name>/?competition_name=<competition_name>

        @type  competition_name: str
        @param competition_name: The competition name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'competition_name' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?competition_name=<competition_name>'},
                            status=status.HTTP_400_BAD_REQUEST)

        competition = get_object_or_404(Competition.objects.all(),
                                        name=request.GET.get('competition_name', ''))
        group = get_object_or_404(Group.objects.all(),
                                  name=kwargs.get('pk'))

        group_enrolled = get_object_or_404(self.queryset, group=group, competition=competition)
        group_enrolled.valid = not group_enrolled.valid
        group_enrolled.save()

        return Response({'status': 'Updated',
                         'message': 'The group inscription has been updated to ' + str(group_enrolled.valid) + ' .'},
                        status=status.HTTP_200_OK)


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
        competition_rounds = Round.objects.filter(parent_competition=competition)

        if len(competition_rounds) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition_rounds.reverse()[0]))

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
        competition_rounds = Round.objects.filter(parent_competition=competition)

        if len(competition_rounds) == 0:
            return Response({'status': 'Bad request',
                             'message': 'Not found '},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(RoundSimplex(competition_rounds[0]))

        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrollGroup(mixins.CreateModelMixin, mixins.DestroyModelMixin,
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
            group = get_object_or_404(Group.objects.all(),
                                      name=serializer.validated_data['group_name'])

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