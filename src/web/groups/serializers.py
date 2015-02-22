from rest_framework import serializers

from authentication.models import Group, GroupMember
from authentication.serializers import AccountSerializer


class GroupSerializer(serializers.ModelSerializer):
    """
    This group serializer allow to CRUD the fields: name and max_members
    """
    class Meta:
        model = Group

        fields = ('name', 'max_members')
        read_only_fields = ('created_at', 'updated_at')


class Member2GroupSerializer(serializers.ModelSerializer):
    """
    This serializer allow to make calls to a specific Group Member. One group member is characterized
    with a username and a group name. This fields depends of the authentication.models.GroupMember attributes.
    """
    user_name = serializers.CharField(max_length=40)
    group_name = serializers.CharField(max_length=128)

    class Meta:
        model = GroupMember
        fields = ('user_name', 'group_name',)


class MemberSerializer(serializers.ModelSerializer):
    """
    This serializer depends of two serializes: AccountSerializer and GroupSerializer. One group member is characterized
    with a Account object, a Group object and a boolean field "is_admin".
    """
    account = AccountSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ('is_admin', 'account', 'group',)
        read_only_fields = ('is_admin',)
