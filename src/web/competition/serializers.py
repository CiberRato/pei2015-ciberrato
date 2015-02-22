from rest_framework import serializers

class SimulationSerializer(serializers.BaseSerializer):
    """
    This serializer is only to retrieve and list methods.
    """
    tmp_folder = "media/tmp_simulations/"

    def to_representation(self, instance):
        return {
            'param_list_path': self.tmp_folder+instance.param_list_path,
            'grid_path': self.tmp_folder+instance.grid_path,
            'lab_path': self.tmp_folder+instance.lab_path,
            'agent_path': self.tmp_folder+instance.agent_path,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
