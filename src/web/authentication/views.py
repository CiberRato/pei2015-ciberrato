import json

from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from authentication.models import Account, GroupMember
from authentication.serializers import AccountSerializer
from authentication.permissions import IsAccountOwner
from django.contrib.auth import authenticate, login, logout


class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        """
        Any operation is permitted only if the user is Authenticated.
        The create method is permitted only too if the user is Authenticated.
        Note: The create method isn't a SAFE_METHOD
        :return:
        :rtype:
        """
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.AllowAny(),

        if self.request.method == 'POST':
            return permissions.AllowAny(),

        return permissions.IsAuthenticated(), IsAccountOwner(),

    def create(self, request):
        """
        B{Create} an user
        B{URL:} ../api/v1/accounts/

        @type  id: number
        @param id: user id
        @type  email: str
        @param email: email
        @type  username: str
        @param username: username
        @type  teaching_institution: str
        @param teaching_institution: teaching institution
        @type  first_name: str
        @param first_name: The first name of user
        @type  last_name: str
        @param last_name: The last name of user
        @type  password: str
        @param password: The password of user
        @type  confirm_password: str
        @param confirm_password: The password confirmation
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            Account.objects.create_user(**serializer.validated_data)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': 'Account could not be created with received data.'
                        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        instance.email = request.data.get('email', instance.email)
        instance.teaching_institution = request.data.get('teaching_institution', instance.teaching_institution)
        instance.first_name = request.data.get('first_name', instance.first_name)
        instance.last_name = request.data.get('last_name', instance.last_name)

        instance.save()

        password = request.data.get('password', None)
        confirm_password = request.data.get('confirm_password', None)

        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
            instance.save()

        return Response({'status': 'Updated',
                         'message': 'Account updated.'
                        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))
        groups = instance.groups.all()

        for group in groups:
            group_member = GroupMember.objects.get(group=group, user=instance)
            if group_member and group_member.is_admin:
                group_members = GroupMember.objects.filter(group=group)
                has_other_admin = False
                for gm in group_members:
                    if gm.is_admin and gm.user != instance:
                        has_other_admin = True
                        break
                if not has_other_admin:
                    group.delete()

        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))
        instance.delete()
        return Response({'status': 'Deleted',
                         'message': 'The account has been deleted.'
                        }, status=status.HTTP_200_OK)


class LoginView(views.APIView):
    def post(self, request):
        """
        B{Login} an user
        B{URL:} ../api/v1/auth/login/
        """
        data = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)

        account = authenticate(email=email, password=password)

        if account is not None:
            if account.is_active:
                login(request, account)

                serialized = AccountSerializer(account)

                return Response(serialized.data)

            else:
                return Response({'status': 'Unauthorized',
                                 'message': 'This account has been disabled.'
                                }, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'status': 'Unauthorized',
                             'message': 'Username and/or password is wrong.'
                            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    def get_permissions(self):
        """
        User needs to be authenticated to logout
        """
        return permissions.IsAuthenticated(),

    def post(self, request):
        """
        B{Logout} an user
        B{URL:} ../api/v1/auth/logout/
        """
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)