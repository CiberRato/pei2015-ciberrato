from rest_framework import serializers


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
