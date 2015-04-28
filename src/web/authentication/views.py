import json

from competition.permissions import IsStaff, IsSuperUser
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import mixins, viewsets, views, status, permissions
from rest_framework.response import Response
from authentication.models import Account, TeamMember
from authentication.serializers import AccountSerializer, AccountSerializerUpdate, PasswordSerializer, \
    AccountSerializerLogin
from authentication.permissions import IsAccountOwner
from django.contrib.auth import authenticate, login, logout
from tokens.models import UserToken
from notifications.models import NotificationTeam


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

        :type  id: number
        :param id: user id
        :type  email: str
        :param email: email
        :type  username: str
        :param username: username
        :type  teaching_institution: str
        :param teaching_institution: teaching institution
        :type  first_name: str
        :param first_name: The first name of user
        :type  last_name: str
        :param last_name: The last name of user
        :type  password: str
        :param password: The password of user
        :type  confirm_password: str
        :param confirm_password: The password confirmation
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            instance = Account.objects.create_user(**serializer.validated_data)
            UserToken.get_or_set(account=instance)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        serializer = AccountSerializerUpdate(data=request.data)

        if serializer.is_valid():
            instance.email = request.data.get('email', instance.email)
            instance.teaching_institution = request.data.get('teaching_institution', instance.teaching_institution)
            instance.first_name = request.data.get('first_name', instance.first_name)
            instance.last_name = request.data.get('last_name', instance.last_name)

            instance.save()

            return Response({'status': 'Updated',
                             'message': 'Account updated.'
                             }, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))
        teams = instance.teams.all()

        for team in teams:
            team_member = TeamMember.objects.get(team=team, account=instance)
            if team_member and team_member.is_admin:
                team_members = TeamMember.objects.filter(team=team)
                has_other_admin = False
                for gm in team_members:
                    if gm.is_admin and gm.account != instance:
                        has_other_admin = True
                        break
                if not has_other_admin:
                    team.delete()

        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))
        instance.delete()
        return Response({'status': 'Deleted',
                         'message': 'The account has been deleted.'
                         }, status=status.HTTP_200_OK)


class AccountChangePassword(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = PasswordSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the password
        B{URL:} ..api/v1/change_password/<username>/

        :type  password: str
        :param password: The password
        :type  confirm_password: str
        :param confirm_password: The confirmation password
        """
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        if instance != request.user:
            return Response({'status': 'Forbidden!',
                             'message': 'Ups, what?'
                             }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            password = request.data.get('password', None)
            confirm_password = request.data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            return Response({'status': 'Updated',
                             'message': 'Account updated.'
                             }, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)


class AccountByFirstName(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} one account by First Name
        B{URL:} ../api/v1/account_by_first_name/<first_name>/

        :type  first_name: str
        :param first_name: The first name
        """
        account = get_list_or_404(self.queryset, first_name=kwargs.get('pk'))
        serializer = self.serializer_class(account, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountByLastName(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Retrieve} one account by Last Name
        B{URL:} ../api/v1/account_by_last_name/<last_name>/

        :type  last_name: str
        :param last_name: The last name
        """
        account = get_list_or_404(self.queryset, last_name=kwargs.get('pk'))
        serializer = self.serializer_class(account, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                if not data.get('remember_me', None):
                    request.session.set_expiry(0)

                login(request, account)

                class Session:
                    def __init__(self, tk, ac):
                        self.token = tk.key
                        self.user = ac

                serialized = AccountSerializerLogin(Session(UserToken.get_or_set(account), account))

                # send notification login!
                for team in account.teams.all():
                    NotificationTeam.add(team=team, status="ok", message=account.username + " has logged in!")

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


class MyDetails(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request):
        """
        See the details of the current logged user
        B{URL:} ..api/v1/me/
        """
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class ToggleUserToStaff(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsStaff(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the user
        B{URL:} ..api/v1/toggle_staff/<username>/

        :type  username: str
        :param username: The username
        """
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        instance.is_staff = not instance.is_staff
        instance.save()

        return Response({'status': 'Updated',
                         'message': 'Account updated, is staff? ' + str(instance.is_staff)
                         }, status=status.HTTP_200_OK)


class ToggleUserToSuperUser(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsSuperUser(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the user
        B{URL:} ..api/v1/toggle_super_user/<username>/

        :type  username: str
        :param username: The username
        """
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        if not instance.is_superuser:
            instance.is_superuser = True
            instance.is_staff = True
        else:
            instance.is_superuser = False

        instance.save()
        return Response({'status': 'Updated',
                         'message': 'Account updated, is super user? ' + str(instance.is_superuser)
                         }, status=status.HTTP_200_OK)


class LoginToOtherUser(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsSuperUser(),

    def retrieve(self, request, *args, **kwargs):
        """
        B{Login to other} user
        B{URL:} ..api/v1/login_to/<username>/

        :type  username: str
        :param username: The username
        """
        account = get_object_or_404(self.queryset, username=kwargs.get('username', ''))
        account.backend = 'django.contrib.auth.backends.ModelBackend'

        logout(request)
        login(request, account)

        serialized = self.serializer_class(account)
        return Response(serialized.data)
