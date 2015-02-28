from competition.models import *
from groups.serializers import *


class CompetitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Competition
        fields = ('name', 'type_of_competition', 'enrolled_groups')
        read_only_fields = ('enrolled_groups',)


class RoundSerializer(serializers.ModelSerializer):
    parent_competition_name = serializers.CharField(max_length=128)

    class Meta:
        model = Round
        fields = ('name', 'parent_competition_name', 'param_list_path', 'grid_path', 'lab_path', 'agents_list')
        read_only_fields = ('param_list_path', 'grid_path', 'lab_path', 'agents_list',)


class GroupEnrolledSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(max_length=128)
    group_name = serializers.CharField(max_length=128)

    class Meta:
        model = GroupEnrolled
        fields = ('competition_name', 'group_name',)

"""
---------------------------------------------------------------
APAGAR A PARTE DA SIMULATION QUANDO AS RONDAS ESTIVEREM PRONTAS
---------------------------------------------------------------
"""
class SimulationSerializer(serializers.BaseSerializer):
    """
    This serializer is only to retrieve and list methods.
    """

    def to_representation(self, instance):
        return {
            'param_list_path': "media/tmp_simulations/Param.xml",
            'grid_path': "media/tmp_simulations/Ciber2010_Grid.xml",
            'lab_path': "media/tmp_simulations/Ciber2010_Lab.xml",
            'agent_path': "media/tmp_simulations/myrob.py"
        }
