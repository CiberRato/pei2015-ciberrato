from rest_framework import serializers
from authentication.models import Account
from rest_framework.validators import ValidationError

from django.core.validators import MinLengthValidator


class AccountSerializer(serializers.ModelSerializer):
    """
    This Account Serializer allow to CRUD the fields: id, email, username, teaching instituition, first name,
    last name, password, confirm_password.
    Create a new user and update user information.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])
    hashkey = serializers.CharField(write_only=True, max_length=40)
    response = serializers.CharField(write_only=True, max_length=32)

    class Meta:
        model = Account
        fields = ('email', 'username', 'teaching_institution', 'first_name', 'last_name', 'password',
                  'confirm_password', 'is_staff', 'is_superuser', 'created_at', 'updated_at', 'hashkey',
                  'response',)
        read_only_fields = ('created_at', 'updated_at')


class AccountSerializerLogin(serializers.BaseSerializer):

    def to_representation(self, instance):
        return {
            'email': instance.user.email,
            'username': instance.user.username,
            'teaching_institution': instance.user.teaching_institution,
            'first_name': instance.user.first_name,
            'last_name': instance.user.first_name,
            'u_stream': instance.token
        }


class PasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])
    confirm_password = serializers.CharField(write_only=True, required=True, validators=[MinLengthValidator(8)])

    class Meta:
        model = Account
        fields = ('password', 'confirm_password',)
        read_only_fields = ()


class EmailSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_internal_value(self, data):
        email = data.get('email')

        # Perform the data validation.
        if not email:
            raise ValidationError({
                'message': 'This field is required.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'email': email
        }


class PasswordResetSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_internal_value(self, data):
        token = data.get('token')
        password = data.get('password')
        confirm_password = data.get('email')

        # Perform the data validation.
        if not token:
            raise ValidationError({
                'message': 'This field is required.'
            })
        if not password:
            raise ValidationError({
                'message': 'This field is required.'
            })
        if not confirm_password:
            raise ValidationError({
                'message': 'This field is required.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'token': token,
            'password': password,
            'confirm_password': confirm_password
        }

