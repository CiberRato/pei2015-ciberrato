from rest_framework import serializers

from authentication.models import Team, TeamMember
from authentication.serializers import AccountSerializer


class TeamSerializer(serializers.ModelSerializer):
    """
    This group serializer allow to CRUD the fields: name and max_members
    """

    class Meta:
        model = Team

        fields = ('name', 'max_members')
        read_only_fields = ('created_at', 'updated_at')


class Member2TeamSerializer(serializers.ModelSerializer):
    """
    This serializer allow to make calls to a specific Team Member. One group member is characterized
    with a username and a group name. This fields depends of the authentication.models.TeamMember attributes.
    """
    user_name = serializers.CharField(max_length=40)
    group_name = serializers.CharField(max_length=128)

    class Meta:
        model = TeamMember
        fields = ('user_name', 'group_name',)


class MemberSerializer(serializers.ModelSerializer):
    """
    This serializer depends of two serializes: AccountSerializer and TeamSerializer. One group member is characterized
    with a Account object, a Team object and a boolean field "is_admin".
    """
    account = AccountSerializer(read_only=True)
    group = TeamSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ('is_admin', 'account', 'group',)
        read_only_fields = ('is_admin',)
