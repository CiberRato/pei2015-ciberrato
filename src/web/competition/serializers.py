from rest_framework import serializers

from competition.models import Simulation
from authentication.serializers import AccountSerializer
from groups.serializers import GroupSerializer


class SimulationSerializer(serializers.ModelSerializer):
    """
    This serializer is only to retrieve and list methods.
    """
    account = AccountSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Simulation

        fields = ('param_list_path', 'grid_path', 'lab_path', 'agent_path', 'created_at', 'updated_at')
        read_only_fields = ('param_list_path', 'grid_path', 'lab_path', 'agent_path', 'created_at', 'updated_at')