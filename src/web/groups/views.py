from django.shortcuts import get_object_or_404

from rest_framework import permissions, viewsets, status, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember, Account
from authentication.serializers import AccountSerializer

from groups.permissions import IsAdminOfGroup
from groups.serializers import GroupSerializer, Member2GroupSerializer, MemberSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.order_by('-name')
    serializer_class = GroupSerializer

    def get_permissions(self):
        """
        Any operation is permitted only if the user is Authenticated.
        The create method is permitted only too if the user is Authenticated.
        Note: The create method isn't a SAFE_METHOD
        The others actions (Destroy) is only permitted if the user IsAdminOfGroup
        :return:
        :rtype:
        """
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        if self.request.method == 'POST':
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def create(self, request, **kwargs):
        """
        B{Create} a group and the GroupMember admin by the user that requested the group create method
        B{URL:} ../api/v1/groups/crud/

        @type  name: str
        @param name: The group name
        @type  max_members: number
        @param max_members: max group members
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            g = Group.objects.create(**serializer.validated_data)
            GroupMember.objects.create(group=g, account=self.request.user, is_admin=True)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': 'The group could not be created with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the group attributes by group name
        B{URL:} ../api/v1/groups/crud/<group_name>/

        @type  pk: str
        @param pk: The group name
        """
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, name=kwargs.get('pk'))
        serializer = self.serializer_class(group)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} the group by a group admin user and delete all the group members
        B{URL:} ../api/v1/groups/crud/<group_name>/

        @type  pk: str
        @param pk: The group name
        """
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, name=kwargs.get('pk'))
        group.delete()
        return Response({'status': 'Deleted',
                         'message': 'The group has been deleted and the group members too.'},
                        status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        B{Update} the group
        B{URL:} ../api/v1/groups/crud/<group_name>/

        @type  pk: str
        @param pk: The group name
        """
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, name=kwargs.get('pk'))

        max_members = request.data.get('max_members', None)
        name = request.data.get('name', None)

        if max_members is not None:
            group.max_members = max_members
        if name is not None:
            group.name = name

        if max_members is None and name is None:
            return Response({'status': 'Bad request',
                             'message': 'The group could not be updated with received data.'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            group.save()

        return Response({'status': 'Updated',
                         'message': 'The group has been updated.'},
                        status=status.HTTP_200_OK)


class AccountGroupsViewSet(mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        """
        If an user wants to see the groups of another user it must be Authenticated.
        :return: True if Authenticated or False if not
        :rtype: permissions.isAuthenticated()
        """
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the groups of an Account
        B{URL:} ../api/v1/groups/user/<username>/
        """
        self.queryset = self.queryset.get(username=kwargs.get('pk'))
        serializer = self.serializer_class(self.queryset.groups, many=True)
        return Response(serializer.data)


class GroupMembersViewSet(mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        """
        If one user wants to see the group members list of one group it must be Authenticated.
        :return: True if Authenticated or False if not
        :rtype: permissions.isAuthenticated()
        """
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the Group members list
        B{URL:} ../api/v1/groups/members/<group_name>/
        """
        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))

        queryset = self.queryset.filter(group=group)
        queryset = [gm.account for gm in queryset]

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class MemberInGroupViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = Member2GroupSerializer

    def get_permissions(self):
        """
        If one user wants to add one user to the group it must be a Admin of the group.
        If one user wants to remove other user from the group it must be a admin of the group.
        The others methods: retrieve it must be only Authenticated.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.IsAuthenticated(),
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def create(self, request, **kwargs):
        """
        B{Create} a GroupMember to a Group
        B{URL:} ../api/v1/groups/member/

        @type  user_name: str
        @param user_name: The user name
        @type  group_name: str
        @param group_name: The group name
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            user = get_object_or_404(Account.objects.all(), username=serializer.validated_data['user_name'])

            already_member = (len(GroupMember.objects.filter(group=group, account=user)) >= 1)

            if already_member:
                return Response({'status': 'Bad request',
                                 'message': 'The user is already in the group'},
                                status=status.HTTP_400_BAD_REQUEST)

            number_of_members = len(GroupMember.objects.filter(group=group))

            if number_of_members >= group.max_members:
                return Response({'status': 'Bad request',
                                 'message': 'The group reached the number max of members:' + str(number_of_members)},
                                status=status.HTTP_400_BAD_REQUEST)

            group_member = GroupMember.objects.create(group=group, account=user)
            group_member_serializer = MemberSerializer(group_member)

            return Response(group_member_serializer.data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad request',
                         'message': 'The group member could not be created with received data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        B{Destroy} a GroupMember from a Group
        B{URL:} ../api/v1/groups/member/<group_name>/?username=<user_name>

        @type  user_name: str
        @param user_name: The user name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the group'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.get(group=group, account=user)
        group_member.delete()

        members = GroupMember.objects.filter(group=group)
        if len(members) == 0:
            group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
            group.delete()

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} the GroupMember of a Group
        B{URL:} ../api/v1/groups/member/<group_name>/?username=<user_name>

        @type  user_name: str
        @param user_name: The user name
        @type  group_name: str
        @param group_name: The group name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the group'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.get(group=group, account=user)
        group_member_serializer = MemberSerializer(group_member)

        return Response(group_member_serializer.data, status=status.HTTP_200_OK)


class MakeMemberAdminViewSet(mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = MemberSerializer

    def get_permissions(self):
        """
        If one user wants to add one user to the admin list of the group it must be a Admin of the group.
        If one user wants to remove other user from the admin list of group it must be a admin of the group.
        The others methods: retrieve it must be only Authenticated.
        """
        return permissions.IsAuthenticated(), IsAdminOfGroup(),

    def update(self, request, *args, **kwargs):
        """
        B{Update}: make admin of the Group
        B{URL:} ../api/v1/groups/admin/<group_name>/?username=<user_name>

        @type  username: str
        @param username: The user name
        @type  pk: str
        @param pk: The group name
        """
        if 'username' not in request.GET:
            return Response({'status': 'Bad request',
                             'message': 'Please provide the ?username=*username*'},
                            status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=kwargs.get('pk'))
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({'status': 'Bad request',
                             'message': 'The user is not in the group'},
                            status=status.HTTP_400_BAD_REQUEST)

        members = GroupMember.objects.filter(group=group)
        num_admins = 0
        for member in members:
            if member.is_admin:
                num_admins += 1

        group_member = GroupMember.objects.get(group=group, account=user)

        if group_member.is_admin and num_admins == 1:
            return Response({'status': 'Bad request',
                             'message': 'The group mast have at least one admin!'},
                            status=status.HTTP_400_BAD_REQUEST)

        group_member.is_admin = not group_member.is_admin
        group_member.save()

        group_member_serializer = MemberSerializer(group_member)

        return Response(group_member_serializer.data, status=status.HTTP_200_OK)