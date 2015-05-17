from rest_framework import serializers


class MediaStatsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'agents': instance.size,
            'grids': instance.grids,
            'json_logs': instance.json_logs,
            'labs': instance.labs,
            'params': instance.params
        }