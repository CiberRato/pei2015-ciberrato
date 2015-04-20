from rest_framework import serializers
from authentication.models import Account

from django.core.validators import MinLengthValidator


class AccountSerializer(serializers.ModelSerializer):
    """
    This Account Serializer allow to CRUD the fields: id, email, username, teaching instituition, first name, 
    last name, password, confirm_password.
    Create a new user and update user information.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])

    class Meta:
        model = Account
        fields = ('email', 'username', 'teaching_institution', 'first_name', 'last_name', 'password',
                  'confirm_password', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class AccountSerializerUpdate(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Account
        fields = ('email', 'username', 'teaching_institution', 'first_name', 'last_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class PasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])

    class Meta:
        model = Account
        fields = ('password', 'confirm_password',)
        read_only_fields = ()