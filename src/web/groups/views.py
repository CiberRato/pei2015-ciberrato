from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework import permissions, viewsets, status, views, mixins
from rest_framework.response import Response

from authentication.models import Group, GroupMember, Account
from authentication.serializers import AccountSerializer

from groups.permissions import IsAdminOfGroup
from groups.serializers import GroupSerializer, UsernameSerializer, Member2GroupSerializer, MemberSerializer

import sys

"""
CREATE:
>> Create a group and the GroupMember adimin by the user that requested the 
group create method
URL: ../api/v1/group/
Params: name and max_members

RETRIEVE:
>> Retrieve the group attributes by group name
URL: ../api/v1/group/<group_name>/

DESTROY:
>> Destroy the group by a group admin user and delete all the group members
URL: ../api/v1/group/<group_name>/
"""
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.order_by('-name')
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        return (permissions.IsAuthenticated(), IsAdminOfGroup(),)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            g = Group.objects.create(**serializer.validated_data)
            GroupMember.objects.create(group=g, account=self.request.user, is_admin=True)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response({
            'status':'Bad request',
            'message': 'The group could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
    	queryset = Group.objects.all()
        group = get_object_or_404(queryset, name=pk)
        serializer = self.serializer_class(group)
        return Response(serializer.data)

    def destroy(self, request, pk):
    	queryset = Group.objects.all()
        group = get_object_or_404(queryset, name=pk)
        group_members = GroupMember.objects.filter(group=group)
        for member in group_members:
        	member.delete()
    	group.delete()
    	return Response({
            'status':'Deleted',
            'message': 'The group has been deleted and the group members too.'
        }, status=status.HTTP_200_OK)

    #update? falta acho...

"""
ONLY RETRIEVE
>> Retrieve the groups of an Account
URL: ../api/v1/user_groups/<username>/
"""
class AccountGroupsViewSet(mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def retrieve(self, request, pk):
        self.queryset = self.queryset.get(username=pk)
        serializer = self.serializer_class(self.queryset.groups, many=True)
        return Response(serializer.data)


"""
ONLY Retrieve
>> Retrieve the Group members list
URL: ../api/v1/group_members/<group_name>/
"""
class GroupMembersViewSet(mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def retrieve(self, request, pk):
        group = get_object_or_404(Group.objects.all(), name=pk)

        queryset = self.queryset.filter(group=group)
        queryset = [gm.account for gm in queryset]

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


"""
CREATE:
>> Create a GroupMember to a Group
URL: ../api/v1/group_member/
Params: user_name and group_name

DESTROY:
>> Destroy a GroupMember from a Group
URL: ../api/v1/group_member/<group_name>/?username=<user_name>

Retrieve:
>> Retrieve the GroupMember of a Group
URL: ../api/v1/group_member/<group_name>/?username=<user_name>
"""
class MemberInGroupViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = Member2GroupSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)
        return (permissions.IsAuthenticated(), IsAdminOfGroup(),)

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            group = get_object_or_404(Group.objects.all(), name=serializer.validated_data['group_name'])
            user = get_object_or_404(Account.objects.all(), username=serializer.validated_data['user_name'])

            already_member = (len(GroupMember.objects.filter(group=group, account=user)) >= 1)

            if already_member:
                return Response({
                    'status':'Bad request',
                    'message': 'The user is already in the group'
                }, status=status.HTTP_400_BAD_REQUEST)

            number_of_members = len(GroupMember.objects.filter(group=group))

            if number_of_members >= group.max_members:
                return Response({
                    'status':'Bad request',
                    'message': 'The group reached the number max of members:'+str(number_of_members)
                }, status=status.HTTP_400_BAD_REQUEST)

            group_member = GroupMember.objects.create(group=group, account=user)
            group_member_serializer = MemberSerializer(group_member)

            return Response(group_member_serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'status':'Bad request',
            'message': 'The group member could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk):
        if 'username' not in request.GET:
            return Response({
                'status':'Bad request',
                'message': 'Please provide the ?username=*username*'
            }, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=pk)
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({
                'status':'Bad request',
                'message': 'The user is not in the group'
            }, status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.get(group=group, account=user)
        group_member.delete()

        return Response(status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk):
        if 'username' not in request.GET:
            return Response({
                'status':'Bad request',
                'message': 'Please provide the ?username=*username*'
            }, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=pk)
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({
                'status':'Bad request',
                'message': 'The user is not in the group'
            }, status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.get(group=group, account=user)
        group_member_serializer = MemberSerializer(group_member)

        return Response(group_member_serializer.data, status=status.HTTP_200_OK)

"""
UPDATE
>> Make admin of the Group
URL: ../api/v1/make_group_admin/<group_name>/?username=<user_name>
"""
class MakeMemberAdminViewSet(mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = MemberSerializer

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOfGroup(),)

    def update(self, request, pk):
        if 'username' not in request.GET:
            return Response({
                'status':'Bad request',
                'message': 'Please provide the ?username=*username*'
            }, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group.objects.all(), name=pk)
        user = get_object_or_404(Account.objects.all(), username=request.GET.get('username', ''))

        member_not_in_group = (len(GroupMember.objects.filter(group=group, account=user)) == 0)

        if member_not_in_group:
            return Response({
                'status':'Bad request',
                'message': 'The user is not in the group'
            }, status=status.HTTP_400_BAD_REQUEST)

        group_member = GroupMember.objects.get(group=group, account=user)
        group_member.is_admin = True
        group_member.save()

        group_member_serializer = MemberSerializer(group_member)

        return Response(group_member_serializer.data, status=status.HTTP_200_OK)
