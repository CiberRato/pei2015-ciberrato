from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from authentication.models import Account
from authentication.serializers import AccountSerializer
from authentication.permissions import IsAccountOwner
from django.contrib.auth import authenticate, login, logout

import json


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
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)

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

        return Response({
        'status': 'Bad Request',
        'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                    }, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username and/or password is wrong.'
                }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(views.APIView):
    """
    User needs to be authenticated to logout
    """
    permission = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        B{Logout} an user
        B{URL:} ../api/v1/auth/logout/
        """
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)