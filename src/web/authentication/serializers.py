from rest_framework import serializers
from authentication.models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    This Account Serializer allow to CRUD the fields: id, email, username, teaching instituition, first name, 
    last name, password, confirm_password.
    Create a new user and update user information.
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'teaching_institution', 'first_name', 'last_name', 'password',
                  'confirm_password')
        read_only_fields = ('created_at', 'updated_at')