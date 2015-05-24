import json

from competition.permissions import IsStaff, IsSuperUser
from django.shortcuts import get_object_or_404, get_list_or_404, render
from rest_framework import mixins, viewsets, views, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from tokens.models import UserToken
from notifications.models import NotificationTeam, NotificationUser
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.db import transaction
from smtplib import SMTPException

from .validation import test_captcha
from .permissions import MustBeStaffUser, UserIsUser, IsAccountOwner
from .models import Account, TeamMember, EmailToken
from .serializers import AccountSerializer, PasswordSerializer, AccountSerializerLogin, EmailSerializer, \
    PasswordResetSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    ## List users
    - #### Method: **GET**
    - #### URL: **/api/v1/accounts/**
    - #### Permissions: **Must be staff user**
    ## Create an user
    - #### Method: **POST**
    - #### URL: **/api/v1/accounts/**
    - #### Parameters: email, username, teaching_institution, first_name, last_name, password, confirm_password
    - #### Permissions: **Allow Any**
    ## Update an user
    - #### Method: **PUT**
    - #### URL: **/api/v1/accounts/&lt;username&gt;/**
    - #### Parameters: email, username, teaching_institution, first_name, last_name
    - #### Permissions: **Is Authenticated and Is Account Owner**
    ## Delete an user
    - #### Method: **DELETE**
    - #### URL: **/api/v1/accounts/&lt;username&gt;/**
    - #### Permissions: **Is Authenticated and Is Account Owner**
    """
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        """
        Any operation is permitted only if the user is Authenticated.
        The create method is permitted only too if the user is Authenticated.
        Note: The create method isn't a SAFE_METHOD

        -> Permissions
        # list
            Must be staff user
        # create
            Allow any
        # destroy and update
            Is Authenticated and Is Account Owner

        :return:
        :rtype:
        """
        if self.request.method == 'POST':
            return permissions.AllowAny(),

        if self.request.method in permissions.SAFE_METHODS:
            return permissions.AllowAny(),

        return permissions.IsAuthenticated(), IsAccountOwner(),

    def list(self, request, *args, **kwargs):
        """
        B{List} users
        B{URL:} ../api/v1/accounts/
        """
        MustBeStaffUser(request.user, 'You don\'t have permissions to see this list!')

        return super(AccountViewSet, self).list(self, request, *args, **kwargs)

    def create(self, request):
        """
        B{Create} an user
        B{URL:} ../api/v1/accounts/

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
            test_captcha(hashkey=serializer.validated_data['hashkey'], response=serializer.validated_data['response'])
            instance = Account.objects.create_user(**serializer.validated_data)
            UserToken.get_or_set(account=instance)

            # send email to confirm the user email
            token = EmailToken.objects.create(user=instance)
            try:
                send_mail('Confirm Your Email Address',
                          'Welcome to CiberRato!\nPlease confirm your email here: ' + settings.CHECK_EMAIL_URL +
                                       str(token.token) + '\nThank you!',
                          'CiberRato <'+settings.EMAIL_HOST_USER+'>',
                          [instance.first_name + " " + instance.last_name + " <" + instance.email + ">"],
                          fail_silently=False,
                          html_message='<h1>Welcome to CiberRato!</h1><h2>Please confirm your email here: <a href="'+
                                       settings.CHECK_EMAIL_URL + str(token.token) + '/">' + settings.CHECK_EMAIL_URL +
                                       str(token.token) + '</a><h2/><br/><h2>Thank you!</h2>')
            except SMTPException:
                return Response({'status': 'Bad Request',
                                 'message': 'The confirmation email could not be sent!'
                                 }, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        serializer = self.serializer_class(instance, data=request.data, partial=True)

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
    """
    ## Change password
    - #### Method: **PUT**
    - #### URL: **/api/v1/change_password/&lt;username&gt;/**
    - #### Parameters: Password and confirm_password
    - #### Permissions: **Is Authenticated and Is Account Owner**
    """
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = PasswordSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(), IsAccountOwner(),

    def update(self, request, *args, **kwargs):
        """
        B{Update} the password
        B{URL:} ../api/v1/change_password/<username>/

        -> Permissions
        # update
            UserIsUser

        :type  password: str
        :param password: The password
        :type  confirm_password: str
        :param confirm_password: The confirmation password
        """
        instance = get_object_or_404(Account.objects.all(), username=kwargs.get('username', ''))

        UserIsUser(user=request.user, instance=instance, message="Ups, what?")

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
    """
    ## Get account by first name
    - #### Method: **GET**
    - #### URL: **/api/v1/account_by_first_name/&lt;first_name&gt;/**
    - #### Permissions: **Is Authenticated**
    """
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
    """
    ## Get account by last name
    - #### Method: **GET**
    - #### URL: **/api/v1/account_by_last_name/&lt;last_name&gt;/**
    - #### Permissions: **Is Authenticated**
    """
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
    """
    ## Login to the platform
    - #### Method: **POST**
    - #### Parameters: **email, password**
    - #### URL: **/api/v1/auth/login/**
    - #### Permissions: **Allow any**
    """
    def post(self, request):
        """
        B{Login} an user
        B{URL:} ../api/v1/auth/login/
        """
        data = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)

        # get user
        accounts = Account.objects.filter(email=email)
        if accounts.count() == 0:
            return Response({'status': 'Unauthorized',
                             'message': 'Username and/or password is wrong.'
                             }, status=status.HTTP_401_UNAUTHORIZED)

        # captcha
        if accounts[0].login_error:
            hashkey = data.get('hashkey', None)
            response = data.get('response', None)
            test_captcha(hashkey=hashkey, response=response)

            accounts[0].login_error = False
            accounts[0].save()

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
                    NotificationTeam.add(team=team, status="info", message=account.username + " has logged in!")

                return Response(serialized.data)

            else:
                return Response({'status': 'Unauthorized',
                                 'message': 'This account has been disabled.'
                                 }, status=status.HTTP_401_UNAUTHORIZED)

        else:
            accounts[0].login_error = True
            accounts[0].save()

            return Response({'status': 'Unauthorized',
                             'message': 'Username and/or password is wrong.'
                             }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    """
    ## Logout from the platform
    - #### Method: **POST**
    - #### URL: **/api/v1/auth/logout/**
    - #### Permissions: **Is authenticated**
    """
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def post(self, request):
        """
        B{Logout} an user
        B{URL:} ../api/v1/auth/logout/
        """
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class MyDetails(views.APIView):
    """
    ## See the details of the current logged user
    - #### Method: **GET**
    - #### URL: **/api/v1/me/**
    - #### Permissions: **Is authenticated**
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request):
        """
        See the details of the current logged user
        B{URL:} ../api/v1/me/
        """
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class ToggleUserToStaff(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    ## Toggle the user to staff member
    - #### Method: **PUT**
    - #### URL: **/api/v1/toggle_staff/&lt;username&gt;/**
    - #### Permissions: **Is authenticated and is staff**
    """
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

        if instance.is_staff:
            NotificationUser.add(user=instance, status="info",
                                 message="Congratulations! Now you are a staff user!")
        else:
            NotificationUser.add(user=instance, status="info",
                                 message="Now you are not a staff user!")

        instance.save()

        return Response({'status': 'Updated',
                         'message': 'Account updated, is staff? ' + str(instance.is_staff)
                         }, status=status.HTTP_200_OK)


class ToggleUserToSuperUser(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    ## Toggle the user to super user
    - #### Method: **PUT**
    - #### URL: **/api/v1/toggle_super_user/&lt;username&gt;/**
    - #### Permissions: **Is authenticated and is super user**
    """
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

        if instance.is_staff:
            NotificationUser.add(user=instance, status="info",
                                 message="Congratulations! Now you are a staff user!")
            NotificationUser.add(user=instance, status="info",
                                 message="Congratulations! Now you are a super user!")
        else:
            NotificationUser.add(user=instance, status="info",
                                 message="Now you are not a super user!")

        instance.save()
        return Response({'status': 'Updated',
                         'message': 'Account updated, is super user? ' + str(instance.is_superuser)
                         }, status=status.HTTP_200_OK)


class LoginToOtherUser(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ## Login to other user
    - #### Method: **GET**
    - #### URL: **/api/v1/login_to/&lt;username&gt;/**
    - #### Permissions: **Is authenticated and is super user**
    """
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


class GetCaptcha(views.APIView):
    """
    ## Get captcha
    - #### Method: **GET**
    - #### URL: **/api/v1/get_captcha/**
    """
    def get_permissions(self):
        return permissions.AllowAny(),

    def get(self, request):
        """
        Get Captcha details
        B{URL:} ..api/v1/get_captcha/
        """
        response = dict()
        response["new_cptch_key"] = CaptchaStore.generate_key()
        response["new_cptch_image"] = captcha_image_url(response['new_cptch_key'])

        return Response(response)


class PasswordRecoverRequest(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = EmailSerializer

    def get_permissions(self):
        return permissions.AllowAny(),

    def create(self, request, *args, **kwargs):
        """
        B{Login to other} user
        B{URL:} ../api/v1/password_recover/request/

        :type  email: str
        :param email: The email
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            account = get_object_or_404(Account.objects.all(), email=serializer.validated_data['email'])

            # send email to confirm the user email
            try:
                with transaction.atomic():
                    token = EmailToken.objects.create(user=account)
            except IntegrityError:
                token = EmailToken.objects.get(user=account)

            try:
                send_mail('Password Recover',
                          'Hello!\nHere is the link to recover your password: ' + settings.PASSWORD_RECOVER_EMAIL_URL +
                                       str(token.token) + '\nThank you!',
                          'CiberRato <' + settings.EMAIL_HOST_USER + '>',
                          [account.first_name + " " + account.last_name + " <" + account.email + ">"],
                          fail_silently=False,
                          html_message='<h1>Hello!!</h1><br/><h2>Here is the link to recover your password: <a href="' +
                                       settings.PASSWORD_RECOVER_EMAIL_URL + str(token.token) + '/">'
                                       + settings.PASSWORD_RECOVER_EMAIL_URL + str(token.token)
                                       + '</a><h2/><br/><h2>Thank you!</h2>')
            except SMTPException:
                return Response({'status': 'Bad Request',
                                 'message': 'The email could not be sent!'
                                 }, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)


class PasswordReset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = PasswordResetSerializer

    def get_permissions(self):
        return permissions.AllowAny(),

    def create(self, request, *args, **kwargs):
        """
        B{PasswordReset}
        B{URL:} ../api/v1/password_recover/reset/

        :type  token: str
        :param token: The token
        :type  password: str
        :param password: The password
        :type  confirm_password: str
        :param confirm_password: The password
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email_token = get_object_or_404(EmailToken.objects.all(),
                                            token=serializer.validated_data['token'])

            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']

            if password and confirm_password and password == confirm_password:
                email_token.user.set_password(password)
                email_token.user.save()
                email_token.delete()

            return Response({'status': 'Updated',
                             'message': 'Account updated.'
                             }, status=status.HTTP_200_OK)

        return Response({'status': 'Bad Request',
                         'message': serializer.errors
                         }, status=status.HTTP_400_BAD_REQUEST)


def check_email(request, token):
    """
    URL: check/email/<token>/
    :param request:
    :type request:
    :param token:
    :type token:
    :return:
    :rtype:
    """
    token = get_object_or_404(EmailToken, token=token)
    token.user.is_active = True
    token.delete()
    return render(request, 'checkEmail.html')